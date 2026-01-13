#!/usr/bin/env python3
"""
Zlib Downloader - Search and download ebooks via Telegram Bot
"""

import os
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

import asyncio
import argparse
import re
import json
from pathlib import Path

try:
    from telethon import TelegramClient
    from telethon.tl.types import DocumentAttributeFilename
except ImportError:
    print("[ERROR] Telethon not installed. Run: pip install telethon")
    sys.exit(1)

from config import (
    TELEGRAM_API_ID, TELEGRAM_API_HASH, ZLIB_BOT_USERNAME,
    SESSION_DIR, DOWNLOAD_DIR,
    DOWNLOAD_TIMEOUT, SEARCH_TIMEOUT, MAX_SEARCH_RESULTS
)


def log(msg: str, level: str = "INFO"):
    icons = {"INFO": "[INFO]", "SUCCESS": "[OK]", "ERROR": "[ERROR]", "WARN": "[WARN]", "STEP": "[STEP]"}
    print(f"{icons.get(level, '')} {msg}")


def get_session_path() -> Path:
    return SESSION_DIR / "telegram"


def sanitize_filename(name: str) -> str:
    """Clean filename"""
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name[:100]


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def parse_search_results(msg) -> list:
    """Parse search results from bot message"""
    results = []
    if not msg.text:
        return results

    text = msg.text
    books_text = re.split(r'📚\s*', text)

    for book_text in books_text[1:]:
        if not book_text.strip():
            continue

        cmd_match = re.search(r'(/book\d+(?:_[a-f0-9]+)?)', book_text)
        if not cmd_match:
            continue
        command = cmd_match.group(1)

        lines = book_text.strip().split('\n')
        title = lines[0].strip().strip('*').strip() if lines else 'Unknown'

        author = ''
        if len(lines) > 1:
            author = lines[1].strip().strip('_').strip()

        language = ''
        lang_match = re.search(r'🌐\s*(\w+)', book_text)
        if lang_match:
            language = lang_match.group(1)

        format_info = ''
        size_info = ''
        fmt_match = re.search(r'\((\w+),\s*([\d.]+\s*[KMG]?B)\)', book_text)
        if fmt_match:
            format_info = fmt_match.group(1).upper()
            size_info = fmt_match.group(2)

        results.append({
            'title': title[:80],
            'author': author[:50],
            'language': language,
            'format': format_info,
            'size': size_info,
            'command': command
        })

        if len(results) >= MAX_SEARCH_RESULTS:
            break

    return results


class ZlibDownloader:
    def __init__(self):
        self.client = None
        self.bot_entity = None
        self.search_results = []
        self.downloaded_file = None

    async def connect(self):
        if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
            log("API credentials not configured", "ERROR")
            return False

        session_path = get_session_path()
        self.client = TelegramClient(str(session_path), TELEGRAM_API_ID, TELEGRAM_API_HASH)
        await self.client.connect()

        if not await self.client.is_user_authorized():
            log("Not authenticated. Run: python tg_auth.py setup", "ERROR")
            return False

        try:
            self.bot_entity = await self.client.get_entity(ZLIB_BOT_USERNAME)
            log(f"Connected to @{ZLIB_BOT_USERNAME}", "SUCCESS")
            return True
        except Exception as e:
            log(f"Cannot find bot: {e}", "ERROR")
            return False

    async def disconnect(self):
        if self.client:
            await self.client.disconnect()

    async def search_book(self, query: str) -> list:
        """Search for books"""
        log(f"Searching: {query}", "STEP")
        self.search_results = []

        await self.client.send_message(self.bot_entity, query)
        await asyncio.sleep(5)

        messages = await self.client.get_messages(self.bot_entity, limit=5)

        for msg in messages:
            if msg.out:
                continue
            if msg.text and '📚' in msg.text:
                results = parse_search_results(msg)
                if results:
                    self.search_results = results
                    break

        log(f"Found {len(self.search_results)} books", "INFO")
        return self.search_results

    def display_results(self):
        """Display search results"""
        if not self.search_results:
            print("\nNo results found.")
            return

        print("\n" + "=" * 70)
        print("Search Results:")
        print("=" * 70)

        for i, r in enumerate(self.search_results):
            print(f"\n  [{i}] {r['title']}")
            if r['author']:
                print(f"      Author: {r['author']}")
            print(f"      {r['language']} | {r['format']} | {r['size']}")

        print("\n" + "=" * 70)

    async def download_book(self, index: int = 0, custom_filename: str = None) -> Path:
        """Download book by sending /book command"""
        if not self.search_results:
            log("No search results", "ERROR")
            return None

        if index >= len(self.search_results):
            log(f"Invalid index: {index}", "ERROR")
            return None

        book = self.search_results[index]
        log(f"Downloading: {book['title']}", "STEP")

        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

        await self.client.send_message(self.bot_entity, book['command'])

        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < DOWNLOAD_TIMEOUT:
            await asyncio.sleep(3)

            messages = await self.client.get_messages(self.bot_entity, limit=5)

            for msg in messages:
                if msg.out:
                    continue

                if msg.document:
                    original_filename = None
                    file_size = msg.document.size or 0

                    for attr in msg.document.attributes:
                        if isinstance(attr, DocumentAttributeFilename):
                            original_filename = attr.file_name
                            break

                    if original_filename:
                        ext = Path(original_filename).suffix

                        if custom_filename:
                            filename = sanitize_filename(custom_filename)
                            if not filename.lower().endswith(ext.lower()):
                                filename += ext
                        else:
                            filename = sanitize_filename(original_filename)

                        filepath = DOWNLOAD_DIR / filename

                        log(f"Receiving file: {filename} ({format_size(file_size)})", "INFO")
                        await self.client.download_media(msg, file=str(filepath))

                        if filepath.exists():
                            actual_size = filepath.stat().st_size
                            log(f"Downloaded: {filepath}", "SUCCESS")
                            log(f"Size: {format_size(actual_size)}", "INFO")
                            self.downloaded_file = filepath
                            return filepath

        log("Download timeout", "ERROR")
        return None

    async def search_and_download(self, query: str, auto_select: bool = True, select_index: int = None) -> Path:
        """Search and download in one step"""
        results = await self.search_book(query)

        if not results:
            log("No books found", "ERROR")
            return None

        self.display_results()

        if auto_select:
            index = 0
            log(f"Auto-selecting first result: {results[0]['title']}", "INFO")
        elif select_index is not None:
            index = select_index
        else:
            try:
                index = int(input("\nSelect book number (0-{}): ".format(len(results) - 1)))
            except (ValueError, EOFError):
                index = 0

        return await self.download_book(index)


async def main_async(args):
    downloader = ZlibDownloader()

    if not await downloader.connect():
        return 1

    try:
        filepath = await downloader.search_and_download(
            args.query,
            auto_select=not args.interactive,
            select_index=args.select
        )

        if filepath:
            result = {
                "success": True,
                "file": str(filepath),
                "size": filepath.stat().st_size
            }
            print("\n--- RESULT JSON ---")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        else:
            return 1

    finally:
        await downloader.disconnect()


def main():
    parser = argparse.ArgumentParser(description='Download ebooks from Zlib via Telegram')
    parser.add_argument('query', help='Book title to search')
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Interactive mode - choose from search results')
    parser.add_argument('-s', '--select', type=int, default=None,
                       help='Select specific result index')
    args = parser.parse_args()

    sys.exit(asyncio.run(main_async(args)))


if __name__ == "__main__":
    main()
