#!/usr/bin/env python3
"""
BookToNotes - Configuration
Edit this file to customize paths for your system.
"""

import os
from pathlib import Path

# =============================================================================
# Telegram API Credentials
# These are Telegram Desktop's public credentials (safe to use)
# You can also get your own from https://my.telegram.org
# =============================================================================
TELEGRAM_API_ID = 2040
TELEGRAM_API_HASH = "b18441a1ff607e10a989891a5462e627"

# =============================================================================
# Zlib Bot Username (without @)
# This is a public Telegram bot for searching ebooks
# =============================================================================
ZLIB_BOT_USERNAME = "zlaboratory_bot"  # Change to your preferred bot

# =============================================================================
# Path Configuration
# Modify these paths according to your system
# =============================================================================

# Base directory (where this skill is installed)
SKILL_DIR = Path(__file__).parent.parent

# Session storage (for Telegram auth)
SESSION_DIR = SKILL_DIR / "data" / "session"

# Download directory for ebooks
DOWNLOAD_DIR = SKILL_DIR / "downloads"

# Output directory for generated notes
OUTPUT_DIR = SKILL_DIR / "output"

# Temporary directory for format conversion
TEMP_DIR = SKILL_DIR / "temp"

# =============================================================================
# External Tools
# =============================================================================

# Calibre ebook-convert path
# Windows: r"C:\Program Files\Calibre2\ebook-convert.exe"
# macOS: "/Applications/calibre.app/Contents/MacOS/ebook-convert"
# Linux: "ebook-convert" (if in PATH)
if os.name == 'nt':  # Windows
    CALIBRE_PATH = r"C:\Program Files\Calibre2\ebook-convert.exe"
else:  # macOS/Linux
    CALIBRE_PATH = "ebook-convert"

# NotebookLM Skill directory (required dependency)
# Install from: https://github.com/anthropics/claude-code-skills
NOTEBOOKLM_SKILL_DIR = Path.home() / ".claude" / "skills" / "notebooklm"

# =============================================================================
# Download Settings
# =============================================================================
DOWNLOAD_TIMEOUT = 120  # seconds
SEARCH_TIMEOUT = 30  # seconds
MAX_SEARCH_RESULTS = 5  # max results to display

# Supported ebook formats (in order of preference)
PREFERRED_FORMATS = ['epub', 'pdf', 'mobi', 'azw3']
