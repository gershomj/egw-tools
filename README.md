# egw — Bible Study in Your Terminal

Search the **King James Bible** and **Ellen G. White's writings** from your command line. Instant KJV lookup. Powerful EGW search. One command to install.

```
egw --kjv "John 3:16"          # Any verse, instantly
egw --search "sanctuary"       # Full-text search across EGW writings
egw --bible "Romans 8:28"      # Every EGW paragraph citing a verse
```

No signup. No API keys. No waiting. KJV works the moment the installer finishes.

---

## Quick Install

### Linux / macOS
```bash
curl -sSL https://raw.githubusercontent.com/gershomj/egw-tools/main/install.sh | bash
```

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/gershomj/egw-tools/main/install.ps1 | iex
```

If Python 3 isn't found, the installer asks permission and installs it for you. Downloads the tool and the KJV database (~12 MB). You're ready in seconds.

---

## What You Can Do

### 🔍 Search EGW Writings

| Command | What it does |
|---|---|
| `egw --search "sabbath school"` | Full-text search (FTS5, ranked, instant) |
| `egw --search "prayer" --book SC` | Search within a specific book |
| `egw --stats "grace"` | See how often a word appears in each book |
| `egw --near "faith works" 10` | Find words within 10 words of each other |
| `egw --topic "sanctuary"` | Search the topical index |
| `egw --concordance "spirit"` | Concordance-style listing |
| `egw --person "James White"` | Find letters and manuscripts mentioning someone |

### 📖 Read and Navigate

| Command | What it does |
|---|---|
| `egw GC 456.1` | Jump to an exact paragraph |
| `egw --chapter GC 41` | Read a full chapter |
| `egw --cite GC 456.1` | Get a formatted citation ready to paste |
| `egw --diff GC GC88 456` | Compare two editions side by side |
| `egw --list` | Browse all available books |
| `egw --info DA` | Book metadata (year, paragraph count) |

### ✝️ KJV Bible (works instantly, no extra download)

| Command | What it does |
|---|---|
| `egw --kjv "John 3:16"` | Look up a verse |
| `egw --kjv "Romans 8:28-30"` | Verse range |
| `egw --kjv-search "living water"` | Search by keyword |
| `egw --kjv-chapter "Psalm 23"` | Read a full chapter |
| `egw --kjv-status` | Database stats (31,009 verses) |

### 🔗 Cross-References

| Command | What it does |
|---|---|
| `egw --bible "John 3:16"` | Find every EGW paragraph citing a verse |
| `egw --bible-stats` | Most-quoted Bible books in EGW |

### 🛠 Maintenance

| Command | What it does |
|---|---|
| `egw --egw-download` | Download the EGW corpus (~1.3 GB) |
| `egw --update` | Update to the latest release |
| `egw --version` | Show current version |
| `egw --help` | See all commands |

---

## EGW Corpus

The KJV Bible works out of the box — 31,009 verses, pre-built, no internet needed after install.

The EGW corpus (~1.3 GB, 1M+ paragraphs) is downloaded on demand. The first time you run any EGW command, the tool asks:

> Download it now? [y/N]

Type `y` and it downloads with a progress bar. You can also trigger this manually:

```
egw --egw-download
```

---

## Coming Soon

**Strong's Concordance** — Hebrew and Greek word lookup directly from KJV verses:

```
egw --kjv "John 3:16" --strongs
```

Definitions, root words, and EGW commentary cross-referenced by original language.

---

## Requirements

- **Python 3.9+** — if missing, the installer offers to get it for you
- That's it. No dependencies. No config files.

Everything lives in `~/.egw-tools/`. To uninstall, delete that folder and remove `egw` from your PATH.

---

## How It Works

### Architecture

The tool is a single Python file with no external dependencies beyond the standard library. It connects to two SQLite databases — one for KJV (12 MB, pre-built and shipped with the installer) and one for EGW (1.3 GB, downloaded on demand from GitHub Releases).

### Search Engine

Both databases use **SQLite FTS5** for full-text search. Queries are ranked by relevance and return in milliseconds across 31K Bible verses and 1M+ EGW paragraphs. The fallback is a standard LIKE scan with proper wildcard escaping — FTS5 catches the vast majority of queries first.

### KJV Database

Pre-built from the public domain King James text. Ships as a 12 MB SQLite database with the following schema:

```
verses        — book_name, book_abbr, chapter, verse, text, reference
verses_fts    — FTS5 index on book_name + text
```

31,009 verses (23,125 OT, 7,884 NT). No build step. No API calls.

### EGW Database

Downloaded from GitHub Releases on demand. Schema:

```
paragraphs       — content with book_code, page, paragraph, chapter_num
paragraphs_fts   — FTS5 full-text index
bible_refs       — verse cross-references (normalized formatting)
topics           — topical index entries
book_index       — per-book metadata
```

The download is a single-file transfer with a progress bar. The database is validated with `PRAGMA integrity_check` on every connection.

### LIKE Safety

All user input that reaches a SQLite LIKE clause is escaped — `%` and `_` wildcards are treated as literal characters, and every LIKE query uses `ESCAPE '\'` to prevent unintended pattern matching.

### Self-Updating

`egw --update` queries the GitHub Releases API, compares version tags, and atomically replaces itself (old version saved as `.bak`).

### Cross-Platform

Pure Python, zero compiled dependencies. Works identically on Linux, macOS, and Windows. The Windows installer creates a `.bat` wrapper for native Command Prompt and PowerShell use.

---

## License

MIT
