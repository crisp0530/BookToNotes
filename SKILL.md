---
name: book-to-notes
description: Smart Book Digestion Engine. One command to download ebooks from Zlib, upload to NotebookLM, and generate structured analysis. Usage: /digest-book or "analyze this book"
---

# BookToNotes - Smart Book Digestion Engine

You are the user's "book digestion engine". Goal: Complete the entire workflow from download to deep analysis with one command.

## Trigger Conditions

When user:
- Uses `/digest-book` command
- Says "analyze this book", "digest book", "deep reading"
- Provides only a book title (no file path) → Download from Zlib
- Provides a book file path → Skip download step

## Core Workflow

```
Phase -1: Zlib Download (optional, only when user provides book title only)
    ↓
Phase 0: Preparation (auto convert to PDF + upload to NotebookLM)
    ↓
Phase 1: Requirements Clarification (analysis mode + focus topic + output audience)
    ↓
Phase 2: Generate Deep Questions (select question framework based on mode)
    ↓
Phase 3: Q&A Loop + Follow-up Mechanism
    ↓
Phase 4: Compile Structured Output
```

---

## All-in-One Preparation Script (Recommended)

Use `prepare.py` to complete download + convert + upload in one step:

```bash
cd ~/.claude/skills/book-to-notes/scripts

# Download from Zlib and upload (auto-select first result)
python prepare.py "Book Title"

# Interactive mode (show search results for selection)
python prepare.py "Book Title" -i

# Use local file (auto format conversion)
python prepare.py --file "path/to/book.epub" --name "Book Name"
```

**Auto-handled**:
- Non-PDF formats auto-converted to PDF (using Calibre)
- Upload to NotebookLM
- Return notebook URL for subsequent Q&A

---

## Step-by-Step Execution (if needed separately)

### Phase -1: Zlib Download

```bash
cd ~/.claude/skills/book-to-notes/scripts
python zlib_download.py "Book Title"           # Auto-select first
python zlib_download.py "Book Title" -i        # Interactive selection
```

### Phase 0: Format Conversion + Upload

If downloaded file is epub/mobi etc., convert to PDF first:
```bash
# Windows
"C:\Program Files\Calibre2\ebook-convert.exe" "input.epub" "output.pdf"

# macOS/Linux
ebook-convert "input.epub" "output.pdf"
```

Then upload to NotebookLM:
```bash
cd ~/.claude/skills/notebooklm
# Windows
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/upload_file.py --file "output.pdf" --name "Book Name" --add-to-library --show-browser

# macOS/Linux
.venv/bin/python scripts/upload_file.py --file "output.pdf" --name "Book Name" --add-to-library --show-browser
```

**Important**: NotebookLM has unstable epub support. Always convert to PDF before uploading.

---

## Phase 1: Requirements Clarification

Before starting analysis, ask user three questions:

1. **Analysis Mode**: Deep understanding / Practical extraction / Both
2. **Focus Topic**: Specific direction user cares about
3. **Output Audience**: Self review / Team sharing / Public article

---

## Phase 2-3: Q&A and Analysis

Use notebooklm skill to ask NotebookLM:

```bash
cd ~/.claude/skills/notebooklm
# Windows
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/ask_question.py --notebook-url "URL" --question "Question"

# macOS/Linux
.venv/bin/python scripts/ask_question.py --notebook-url "URL" --question "Question"
```

### Deep Understanding Mode Question Framework (15-20 questions)
- Core thesis, key concepts, structure analysis
- Author background, historical context, implicit assumptions
- Argumentation methods, key pillars
- Overall assessment, intellectual legacy

### Practical Extraction Mode Question Framework (12-15 questions)
- Core arguments, frameworks/models, methodology
- Case studies, counterexamples/boundaries, common misconceptions
- Action checklist

---

## Phase 4: Compile Output

Save to `output/` directory:
- `{BookName}_deep_notes.md` - Structured article

---

## Quick Command Reference

### All-in-One Preparation
```bash
cd ~/.claude/skills/book-to-notes/scripts
python prepare.py "Book Title"                    # Download + convert + upload
python prepare.py --file "book.epub"              # Local file upload
```

### Telegram Authentication
```bash
cd ~/.claude/skills/book-to-notes/scripts
python tg_auth.py status
python tg_auth.py setup
```

### NotebookLM Authentication
```bash
cd ~/.claude/skills/notebooklm
# Windows
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/auth_manager.py status
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/auth_manager.py setup

# macOS/Linux
.venv/bin/python scripts/auth_manager.py status
.venv/bin/python scripts/auth_manager.py setup
```

---

## Dependencies

- **Telethon**: `pip install telethon`
- **Calibre**: https://calibre-ebook.com/
- **NotebookLM Skill**: `~/.claude/skills/notebooklm`

---

## Notes

1. **First-time use requires authentication**: Telegram + Google (NotebookLM)
2. **Always convert to PDF**: Direct epub upload may fail
3. **NotebookLM has daily Q&A limits**
4. **Check downloaded files**: Confirm it's the correct book
