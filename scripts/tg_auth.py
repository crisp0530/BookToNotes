#!/usr/bin/env python3
"""
Telegram Authentication Script
First-time login to Telegram and save session
"""

import os
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

import asyncio
import argparse
from pathlib import Path

try:
    from telethon import TelegramClient
    from telethon.errors import SessionPasswordNeededError
except ImportError:
    print("[ERROR] Telethon not installed. Run: pip install telethon")
    sys.exit(1)

from config import (
    TELEGRAM_API_ID, TELEGRAM_API_HASH,
    SESSION_DIR
)


def log(msg: str, level: str = "INFO"):
    icons = {"INFO": "[INFO]", "SUCCESS": "[OK]", "ERROR": "[ERROR]", "WARN": "[WARN]", "STEP": "[STEP]"}
    print(f"{icons.get(level, '')} {msg}")


def get_session_path() -> Path:
    """Get session file path"""
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    return SESSION_DIR / "telegram"


async def check_auth() -> bool:
    """Check if authenticated"""
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        log("API credentials not configured in config.py", "ERROR")
        return False

    session_path = get_session_path()
    client = TelegramClient(str(session_path), TELEGRAM_API_ID, TELEGRAM_API_HASH)

    try:
        await client.connect()
        if await client.is_user_authorized():
            me = await client.get_me()
            log(f"Authenticated as: {me.first_name} (@{me.username})", "SUCCESS")
            return True
        else:
            log("Not authenticated", "WARN")
            return False
    except Exception as e:
        log(f"Auth check failed: {e}", "ERROR")
        return False
    finally:
        await client.disconnect()


async def setup_auth():
    """Interactive Telegram login"""
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        log("Please configure TELEGRAM_API_ID and TELEGRAM_API_HASH in config.py", "ERROR")
        log("Get them from https://my.telegram.org", "INFO")
        return False

    session_path = get_session_path()
    client = TelegramClient(str(session_path), TELEGRAM_API_ID, TELEGRAM_API_HASH)

    try:
        await client.connect()

        if await client.is_user_authorized():
            me = await client.get_me()
            log(f"Already authenticated as: {me.first_name}", "SUCCESS")
            return True

        log("Starting Telegram login...", "STEP")
        phone = input("Enter your phone number (with country code, e.g., +1xxx): ")

        await client.send_code_request(phone)
        log("Verification code sent", "INFO")

        code = input("Enter the verification code: ")

        try:
            await client.sign_in(phone, code)
        except SessionPasswordNeededError:
            log("Two-factor authentication enabled", "INFO")
            password = input("Enter your 2FA password: ")
            await client.sign_in(password=password)

        me = await client.get_me()
        log(f"Login successful! Welcome, {me.first_name}", "SUCCESS")
        log(f"Session saved to: {session_path}.session", "INFO")
        return True

    except Exception as e:
        log(f"Login failed: {e}", "ERROR")
        return False
    finally:
        await client.disconnect()


async def logout():
    """Logout and delete session"""
    session_path = get_session_path()
    session_file = Path(f"{session_path}.session")

    if session_file.exists():
        session_file.unlink()
        log("Session deleted", "SUCCESS")
    else:
        log("No session found", "WARN")


def main():
    parser = argparse.ArgumentParser(description='Telegram Authentication Manager')
    parser.add_argument('action', choices=['status', 'setup', 'logout'],
                       help='Action to perform')
    args = parser.parse_args()

    if args.action == 'status':
        asyncio.run(check_auth())
    elif args.action == 'setup':
        asyncio.run(setup_auth())
    elif args.action == 'logout':
        asyncio.run(logout())


if __name__ == "__main__":
    main()
