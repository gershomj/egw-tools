# egw — Your Personal Bible Study CLI

Search the **King James Bible** and **Ellen G. White's writings** from your terminal. One command to install. Nothing to configure. KJV works instantly — no build step, no waiting, no internet required after install.

```
egw --kjv "John 3:16"          # Look up any KJV verse
egw --search "sanctuary"       # Search EGW corpus instantly
egw --bible "Revelation 13"    # Find every EGW quote on a verse
```

---

## Install

### Linux / macOS
```bash
curl -sSL https://raw.githubusercontent.com/gershomj/egw-tools/main/install.sh | bash
```

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/gershomj/egw-tools/main/install.ps1 | iex
```

The installer downloads `egw` and the pre-built KJV database (~12 MB). If Python 3 isn't found, it offers to install it for you. You're ready to go in seconds.

---

## What You Can Do

### KJV Bible (works immediately, no extra download)

| Command | What it does |
|---|---|
| `egw --kjv "John 3:16"` | Look up a verse |
| `egw --kjv "Romans 8:28-30"` | Verse range |
| `egw --kjv-search "living water"` | Search by keyword or phrase |
| `egw --kjv-chapter "Psalm 23"` | Read a full chapter |
| `egw --kjv-status` | Database info (31,009 verses) |

### EGW Writings (requires corpus download — the tool prompts you)

| Command | What it does |
|---|---|
| `egw --search "sabbath school"` | Full-text search |
| `egw --search "prayer" --book SC` | Search within a specific book |
| `egw --bible "John 3:16"` | Find paragraphs that cite a Bible verse |
| `egw --bible-stats` | See which Bible books are quoted most |
| `egw --stats "grace"` | See term frequency across all books |
| `egw --near "faith works" 10` | Find words near each other |
| `egw --topic "sanctuary"` | Search the topical index |
| `egw --chapter GC 41` | Read a full chapter |
| `egw --cite GC 456.1` | Get a formatted citation |
| `egw --person "James White"` | Find letters mentioning someone |
| `egw --list` | Browse all available books |
| `egw GC 456.1` | Jump to an exact paragraph |

### Maintenance

| Command | What it does |
|---|---|
| `egw --egw-download` | Download EGW corpus (~1.3 GB, optional) |
| `egw --update` | Update to the latest release |
| `egw --version` | Show your current version |
| `egw --help` | See all commands |

---

## Coming in the Next Release

**Strong's Concordance integration** — look up original Hebrew and Greek words directly from KJV verses, with definitions, root meanings, and cross-references to EGW commentary on specific words. `egw --kjv "John 3:16" --strongs` is on the way.

---

## Requirements

- **Python 3.9+** — the installer finds it automatically. If missing, it offers to install via your package manager (apt, pacman, brew, dnf, winget). Or grab it from [python.org](https://python.org).
- That's it. No pip packages, no Docker, no API keys, no configuration files.

Everything lives in `~/.egw-tools/`. Uninstall by deleting that folder and removing `egw` from your PATH.

---

## EGW Corpus

KJV works out of the box. When you first run any EGW command (like `--search`), the tool asks if you want to download the EGW corpus (~1.3 GB) from GitHub Releases. You can also trigger this manually with:

```
egw --egw-download
```

The download is resumable — if interrupted, just run it again.

---

## How It Works (Technical Details)

### KJV: Pre-Built, Instant
The KJV database ships pre-built with the installer (31,009 verses, 12 MB SQLite database with FTS5 full-text indexing). No background build process. No external API calls. No waiting. First `--kjv` command works instantly, and KJV features work completely offline after install.

### EGW: On-Demand Download
The EGW corpus (~1.3 GB, 1M+ paragraphs) is downloaded from GitHub Releases when you choose to. Once downloaded, all EGW features work fully offline. The prompt is clear about the size and asks permission before downloading.

### Search Engine
Both databases use **SQLite FTS5** — the same full-text engine that powers major applications. Searches are ranked by relevance and return in milliseconds.

### Self-Updating
`egw --update` queries the GitHub Releases API for the latest version tag and atomically replaces itself (old version saved as `.bak`). This is the only automatic internet connection — everything else requires your explicit action.

### Cross-Platform
Pure Python with zero compiled dependencies. Works identically on Linux, macOS, and Windows. The Windows installer creates a `.bat` wrapper so `egw` works natively in Command Prompt and PowerShell.

### Database Schema

**KJV** (`kjv.db`):
- `verses` — book_name, book_abbr, chapter, verse, text, reference
- `verses_fts` — FTS5 full-text index on book_name + text

**EGW** (`egw-corpus.db`):
- `paragraphs` — content with book_code, page, paragraph, chapter_num
- `paragraphs_fts` — FTS5 full-text index
- `bible_refs` — verse cross-references with normalized formatting
- `topics` — topical index entries
- `book_index` — per-book metadata

---

## License

MIT — use it however you want.
