# egw — Your Personal Bible Study CLI

Search the **King James Bible** and **Ellen G. White's writings** from your terminal. One command to install. Nothing to configure. It just works.

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

That's it. The installer finds Python, downloads everything, adds `egw` to your PATH, and starts building the KJV database in the background. You can use the tool right away.

---

## What You Can Do

### KJV Bible
| Command | What it does |
|---|---|
| `egw --kjv "John 3:16"` | Look up a verse |
| `egw --kjv "Romans 8:28-30"` | Verse range |
| `egw --kjv-search "living water"` | Search by keyword or phrase |
| `egw --kjv-chapter "Psalm 23"` | Read a full chapter |

### EGW Writings
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
| `egw --kjv-status` | Check KJV database build progress |
| `egw --update` | Update to the latest release |
| `egw --version` | Show your current version |
| `egw --help` | See all commands |

---

## Coming in the Next Release

**Strong's Concordance integration** — look up original Hebrew and Greek words directly from KJV verses, with definitions, root meanings, and cross-references to EGW commentary on specific words. `egw --kjv "John 3:16" --strongs` is on the way.

---

## Requirements

- **Python 3.9+** — the installer finds it automatically. If it's missing, install from [python.org](https://python.org) or your package manager.
- That's it. No pip packages, no Docker, no API keys, no configuration files.

Everything lives in `~/.egw-tools/`. Uninstall by deleting that folder and removing `egw` from your PATH.

---

## EGW Database

KJV works out of the box. For EGW features, you'll need an `egw-corpus.db` placed in `~/.egw-tools/`. The tool will tell you where to put it if it's missing.

---

## How It Works (Technical Details)

### Zero-Config Architecture
The tool auto-detects its home directory (`~/.egw-tools/`) and creates it on first run. No environment variables needed — everything uses sensible defaults. The KJV database builds silently in the background via a detached subprocess, so your terminal isn't tied up.

### Search Engine
Both databases use **SQLite FTS5** — the same full-text engine that powers major applications. Searches are ranked by relevance and return in milliseconds across 1M+ EGW paragraphs and 31K+ Bible verses.

### KJV Auto-Build
The first time you run any `--kjv` command, `build_kjv.py` launches in the background and downloads all 1,189 chapters from the free bible-api.com service, indexes them with FTS5, and writes the result to `~/.egw-tools/kjv.db` (~3 MB). Takes about 40 minutes. Check progress with `egw --kjv-status`. The builder is resumable — if it gets interrupted, it picks up where it left off.

### Self-Updating
`egw --update` queries the GitHub Releases API for the latest version tag, compares it against the running version, downloads the new binary if newer, and atomically replaces itself (old version saved as `.bak`).

### Cross-Platform
Pure Python with zero compiled dependencies. Works identically on Linux, macOS, and Windows. The Windows installer creates a `.bat` wrapper so `egw` works natively in Command Prompt and PowerShell.

### Database Schema
The EGW corpus database expects these tables:
- `paragraphs` — content with book_code, page, paragraph, chapter_num
- `paragraphs_fts` — FTS5 full-text index
- `bible_refs` — verse cross-references with normalized formatting
- `topics` — topical index entries
- `book_index` — per-book metadata

The KJV database (`kjv.db`) is built automatically. Schema: `verses` (book_name, book_abbr, chapter, verse, text, reference) with `verses_fts` for full-text indexing.

---

## License

MIT — use it however you want.
