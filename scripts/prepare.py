#!/usr/bin/env python3
"""
BookToNotes - All-in-one Preparation Script
Integrates: Zlib download + Format conversion + Upload to NotebookLM

Usage:
  python prepare.py "book title"                    # Download from Zlib and upload
  python prepare.py "book title" -i                 # Interactive mode
  python prepare.py --file "path/to/book.epub" --name "Book Name"  # Local file
"""

import os
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

import subprocess
import argparse
import re
import json
import shutil
import asyncio
from pathlib import Path

from config import (
    CALIBRE_PATH, NOTEBOOKLM_SKILL_DIR,
    DOWNLOAD_DIR, OUTPUT_DIR, TEMP_DIR
)

# Supported ebook formats
SUPPORTED_FORMATS = ['.epub', '.pdf', '.mobi', '.azw', '.azw3', '.txt', '.docx']


def log(msg: str, level: str = "INFO"):
    icons = {
        "INFO": "[INFO]",
        "SUCCESS": "[OK]",
        "ERROR": "[ERROR]",
        "WARN": "[WARN]",
        "STEP": "[STEP]"
    }
    print(f"{icons.get(level, '')} {msg}")


def get_subprocess_env():
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    return env


def check_dependencies():
    """Check required dependencies"""
    log("Checking dependencies...", "STEP")

    # Check Calibre
    calibre_path = Path(CALIBRE_PATH)
    if not calibre_path.exists() and os.name == 'nt':
        log(f"Calibre not found: {CALIBRE_PATH}", "ERROR")
        log("Please install Calibre from https://calibre-ebook.com/", "INFO")
        return False

    # Check NotebookLM skill
    if not NOTEBOOKLM_SKILL_DIR.exists():
        log(f"NotebookLM Skill not found: {NOTEBOOKLM_SKILL_DIR}", "ERROR")
        log("Please install the NotebookLM skill first", "INFO")
        return False

    # Check NotebookLM venv
    if os.name == 'nt':
        venv_python = NOTEBOOKLM_SKILL_DIR / ".venv" / "Scripts" / "python.exe"
    else:
        venv_python = NOTEBOOKLM_SKILL_DIR / ".venv" / "bin" / "python"

    if not venv_python.exists():
        log("NotebookLM venv not initialized", "ERROR")
        return False

    log("Dependencies OK", "SUCCESS")
    return True


def download_from_zlib(query: str, interactive: bool = False) -> Path:
    """Download book from Zlib"""
    log(f"Downloading from Zlib: {query}", "STEP")

    try:
        from zlib_download import ZlibDownloader
    except ImportError:
        log("Cannot import zlib_download module", "ERROR")
        return None

    async def do_download():
        downloader = ZlibDownloader()
        if not await downloader.connect():
            return None

        try:
            filepath = await downloader.search_and_download(
                query,
                auto_select=not interactive,
                select_index=None
            )
            return filepath
        finally:
            await downloader.disconnect()

    filepath = asyncio.run(do_download())

    if filepath and filepath.exists():
        log(f"Downloaded: {filepath}", "SUCCESS")
        return filepath
    else:
        log("Download failed", "ERROR")
        return None


def convert_to_pdf(input_file: Path, book_name: str) -> Path:
    """Convert to PDF format if not already PDF"""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    output_file = TEMP_DIR / f"{book_name}.pdf"

    # If already PDF, just copy
    if input_file.suffix.lower() == '.pdf':
        log("File is already PDF, copying...", "INFO")
        shutil.copy(input_file, output_file)
        log(f"Copied to: {output_file}", "SUCCESS")
        return output_file

    # Otherwise convert with Calibre
    log(f"Converting {input_file.suffix} -> PDF...", "STEP")

    cmd = [CALIBRE_PATH, str(input_file), str(output_file)]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    if result.returncode != 0:
        log(f"Conversion failed: {result.stderr[:200]}", "ERROR")
        return None

    if output_file.exists():
        log(f"Converted: {output_file}", "SUCCESS")
        return output_file
    else:
        log("Conversion failed: output file not created", "ERROR")
        return None


def upload_to_notebooklm(pdf_file: Path, book_name: str) -> tuple:
    """Upload to NotebookLM"""
    log(f"Uploading to NotebookLM: {book_name}", "STEP")

    if os.name == 'nt':
        venv_python = NOTEBOOKLM_SKILL_DIR / ".venv" / "Scripts" / "python.exe"
    else:
        venv_python = NOTEBOOKLM_SKILL_DIR / ".venv" / "bin" / "python"

    upload_script = NOTEBOOKLM_SKILL_DIR / "scripts" / "upload_file.py"

    result = subprocess.run(
        [
            str(venv_python),
            str(upload_script),
            "--file", str(pdf_file),
            "--name", book_name,
            "--add-to-library",
            "--show-browser"
        ],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        env=get_subprocess_env()
    )

    output = result.stdout + result.stderr
    print(output)

    # Extract notebook URL
    url_match = re.search(
        r'Notebook URL: (https://notebooklm\.google\.com/notebook/[a-zA-Z0-9_-]+)',
        output
    )
    notebook_url = url_match.group(1) if url_match else None

    # Extract notebook ID
    id_match = re.search(r'Notebook ID: ([a-zA-Z0-9_-]+)', output)
    notebook_id = id_match.group(1) if id_match else None

    if notebook_url:
        log("Upload success!", "SUCCESS")
        log(f"  URL: {notebook_url}", "INFO")
        log(f"  ID: {notebook_id}", "INFO")
        return notebook_id, notebook_url
    else:
        if "already exists" in output:
            log("Notebook already exists", "WARN")
            library_id = book_name.lower().replace(' ', '-').replace('_', '-')
            return library_id, None

        log("Upload failed", "ERROR")
        return None, None


def prepare_book(query: str = None, file_path: str = None, book_name: str = None, interactive: bool = False):
    """
    Complete book preparation workflow

    Args:
        query: Book title (for Zlib download)
        file_path: Local file path
        book_name: Custom book name
        interactive: Interactive mode for search results
    """
    print("\n" + "=" * 60)
    print("BookToNotes - Preparation")
    print("=" * 60 + "\n")

    # Check dependencies
    if not check_dependencies():
        return None

    # Determine input file
    input_file = None

    if file_path:
        # Use local file
        input_file = Path(file_path)
        if not input_file.exists():
            log(f"File not found: {input_file}", "ERROR")
            return None
        if input_file.suffix.lower() not in SUPPORTED_FORMATS:
            log(f"Unsupported format: {input_file.suffix}", "ERROR")
            log(f"Supported: {', '.join(SUPPORTED_FORMATS)}", "INFO")
            return None
        log(f"Using local file: {input_file}", "INFO")

    elif query:
        # Download from Zlib
        input_file = download_from_zlib(query, interactive)
        if not input_file:
            return None

    else:
        log("Please provide either a search query or a file path", "ERROR")
        return None

    # Determine book name
    if not book_name:
        book_name = input_file.stem
        book_name = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', book_name)[:50]

    log(f"Book name: {book_name}", "INFO")

    # Convert to PDF
    pdf_file = convert_to_pdf(input_file, book_name)
    if not pdf_file:
        return None

    # Upload to NotebookLM
    notebook_id, notebook_url = upload_to_notebooklm(pdf_file, book_name)
    if not notebook_id:
        return None

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Output results
    print("\n" + "=" * 60)
    print("Preparation Complete!")
    print("=" * 60)
    print(f"\nBook Name: {book_name}")
    print(f"Source File: {input_file}")
    print(f"PDF File: {pdf_file}")
    print(f"Notebook ID: {notebook_id}")
    if notebook_url:
        print(f"Notebook URL: {notebook_url}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print("=" * 60 + "\n")

    result = {
        "success": True,
        "book_name": book_name,
        "source_file": str(input_file),
        "pdf_file": str(pdf_file),
        "notebook_id": notebook_id,
        "notebook_url": notebook_url,
        "output_dir": str(OUTPUT_DIR)
    }

    print("--- RESULT JSON ---")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return result


def main():
    parser = argparse.ArgumentParser(
        description='BookToNotes - Prepare book for analysis',
        epilog='After preparation, use Claude Code to analyze the book via NotebookLM.'
    )
    parser.add_argument('query', nargs='?', help='Book title to search on Zlib')
    parser.add_argument('--file', '-f', help='Local ebook file path')
    parser.add_argument('--name', '-n', help='Custom book name')
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Interactive mode - choose from search results')
    args = parser.parse_args()

    if not args.query and not args.file:
        parser.print_help()
        print("\nError: Please provide either a book title or --file path")
        sys.exit(1)

    result = prepare_book(
        query=args.query,
        file_path=args.file,
        book_name=args.name,
        interactive=args.interactive
    )

    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
