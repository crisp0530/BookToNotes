# BookToNotes

[中文文档](README.zh-CN.md) | English

> One command to transform any book into structured notes using AI.

BookToNotes is a Claude Code skill that automates the entire book reading workflow:
**Search → Download → Convert → Upload to NotebookLM → AI-powered Q&A → Structured Notes**

## Features

- **One-command workflow**: Just provide a book title, get structured notes
- **Zlib integration**: Search and download ebooks via Telegram bot
- **Format conversion**: Auto-convert epub/mobi/azw to PDF using Calibre
- **NotebookLM integration**: Upload books and perform AI-powered Q&A
- **Structured output**: Generate comprehensive notes with customizable depth

## Prerequisites

Before using BookToNotes, you need:

1. **Claude Code** - [Install Claude Code CLI](https://github.com/anthropics/claude-code)
2. **Calibre** - [Download Calibre](https://calibre-ebook.com/) for ebook format conversion
3. **Telegram account** - For accessing Zlib bot
4. **Google account** - For NotebookLM access
5. **NotebookLM Skill** - Install the NotebookLM skill for Claude Code

## Installation

### 1. Clone this repository

```bash
# Navigate to Claude Code skills directory
cd ~/.claude/skills

# Clone the repository
git clone https://github.com/YOUR_USERNAME/BookToNotes.git book-to-notes
```

### 2. Install Python dependencies

```bash
cd ~/.claude/skills/book-to-notes/scripts
pip install telethon
```

### 3. Configure paths (if needed)

Edit `scripts/config.py` to customize paths for your system:

```python
# Calibre path (adjust for your OS)
CALIBRE_PATH = r"C:\Program Files\Calibre2\ebook-convert.exe"  # Windows
# CALIBRE_PATH = "/Applications/calibre.app/Contents/MacOS/ebook-convert"  # macOS
# CALIBRE_PATH = "ebook-convert"  # Linux (if in PATH)
```

### 4. Authenticate services

#### Telegram (for Zlib download)
```bash
cd ~/.claude/skills/book-to-notes/scripts
python tg_auth.py setup
```

#### NotebookLM (for AI Q&A)
```bash
cd ~/.claude/skills/notebooklm
.venv/Scripts/python.exe scripts/auth_manager.py setup  # Windows
# .venv/bin/python scripts/auth_manager.py setup  # macOS/Linux
```

## Usage

### In Claude Code

Simply tell Claude what book you want to analyze:

```
> Analyze "Thinking, Fast and Slow"
> /digest-book "The Lean Startup"
> Help me digest "Atomic Habits"
```

### Command Line

```bash
cd ~/.claude/skills/book-to-notes/scripts

# Download from Zlib and process
python prepare.py "Book Title"

# Interactive mode (choose from search results)
python prepare.py "Book Title" -i

# Use local file
python prepare.py --file "path/to/book.epub" --name "Book Name"
```

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    BookToNotes Workflow                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. INPUT                                                    │
│     ├── Book title → Search & download from Zlib            │
│     └── Local file → Skip to conversion                     │
│                                                              │
│  2. CONVERT                                                  │
│     └── epub/mobi/azw → PDF (via Calibre)                   │
│                                                              │
│  3. UPLOAD                                                   │
│     └── PDF → NotebookLM                                    │
│                                                              │
│  4. ANALYZE                                                  │
│     ├── Clarify requirements (mode, focus, audience)        │
│     ├── Generate deep questions                             │
│     └── Q&A loop with NotebookLM                            │
│                                                              │
│  5. OUTPUT                                                   │
│     └── Structured markdown notes                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Analysis Modes

### Deep Understanding Mode
- Core thesis and key concepts
- Author background and historical context
- Argumentation methods and logical structure
- Critical assessment and intellectual legacy

### Practical Extraction Mode
- Actionable frameworks and models
- Case studies and examples
- Common misconceptions
- Implementation checklist

## Project Structure

```
book-to-notes/
├── SKILL.md              # Claude Code skill definition
├── README.md             # This file
├── scripts/
│   ├── config.py         # Configuration (paths, settings)
│   ├── tg_auth.py        # Telegram authentication
│   ├── zlib_download.py  # Zlib search & download
│   └── prepare.py        # All-in-one preparation script
├── downloads/            # Downloaded ebooks (gitignored)
├── temp/                 # Converted PDFs (gitignored)
├── output/               # Generated notes (gitignored)
└── data/
    └── session/          # Auth sessions (gitignored)
```

## Configuration

All configuration is in `scripts/config.py`:

| Setting | Description | Default |
|---------|-------------|---------|
| `TELEGRAM_API_ID` | Telegram API ID | 2040 (public) |
| `TELEGRAM_API_HASH` | Telegram API Hash | (public) |
| `ZLIB_BOT_USERNAME` | Zlib Telegram bot | zlaboratory_bot |
| `CALIBRE_PATH` | Path to ebook-convert | OS-dependent |
| `DOWNLOAD_TIMEOUT` | Download timeout (seconds) | 120 |
| `MAX_SEARCH_RESULTS` | Max search results shown | 5 |

## Troubleshooting

### "Calibre not found"
- Install Calibre from https://calibre-ebook.com/
- Update `CALIBRE_PATH` in `config.py`

### "Not authenticated" (Telegram)
```bash
python tg_auth.py setup
```

### "NotebookLM venv not initialized"
- Ensure NotebookLM skill is properly installed
- Run the NotebookLM setup script

### "Upload failed"
- NotebookLM has unstable epub support - always convert to PDF first
- Check your Google account authentication

## Privacy & Security

- **No personal data stored**: All paths are configurable
- **Session files are local**: Telegram/Google sessions stay on your machine
- **Gitignored sensitive dirs**: downloads/, data/, output/ are not tracked

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- [Calibre](https://calibre-ebook.com/) for ebook conversion
- [Telethon](https://github.com/LonamiWebs/Telethon) for Telegram API
- [NotebookLM](https://notebooklm.google.com/) for AI-powered document analysis
