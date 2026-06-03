# EGW Research Suite

FTS5-powered command-line research tool for **Ellen G. White writings** and the **King James Bible**.

```
egw --search "sanctuary"       # Full-text search EGW corpus
egw --kjv "John 3:16"          # Look up a KJV verse
egw --kjv-search "faith hope"  # Search KJV by keyword
egw --bible "Revelation 13"    # Find EGW quoting a verse
egw GC 456.1                   # Exact paragraph lookup
```

## Features

### EGW Corpus Search
- **FTS5 full-text search** with ranking — 1M+ paragraphs across 758 works
- **84K Bible cross-references** — find every EGW quote citing a specific verse
- **72K topics** — browse or search the topical index
- **Proximity search** — find words within N words of each other
- **Exact lookup** — `egw GC 456.1` → instant paragraph
- **Chapter view**, **concordance**, **frequency stats**, **edition comparison**
- **Person search** — find letters/manuscripts mentioning someone

### KJV Bible
- **Verse lookup** — `egw --kjv "John 3:16-18"` with range support
- **FTS5 keyword search** — `egw --kjv-search "faith hope charity"`
- **Full chapter** — `egw --kjv-chapter "Psalm 23"`
- All 66 books, 31,102 verses, authorized King James text

### Self-Updating
- `egw --update` checks GitHub releases and installs the latest version
- `egw --version` shows current version

## Install

```bash
# Download the script
curl -O https://raw.githubusercontent.com/gershomj/egw-tools/main/egw
chmod +x egw
sudo mv egw /usr/local/bin/

# Build the KJV Bible database (~3 MB, takes ~40 min)
python3 build_kjv.py
```

## Database Setup

The tool needs SQLite databases to search. Set paths via environment variables:

```bash
export EGW_DB=/path/to/egw-corpus.db    # default: ~/.hermes/egw-corpus.db
export KJV_DB=/path/to/kjv.db           # default: ~/.hermes/kjv.db
```

### KJV Bible
Run `build_kjv.py` to download and index the complete KJV from the free bible-api.com service. Requires Python 3.9+ and the `requests` library. The resulting database is ~3 MB with FTS5 indexing.

### EGW Corpus
The EGW database must be built separately from EGW text sources. The expected schema:

| Table | Purpose |
|---|---|
| `paragraphs` | Main content with book_code, page, paragraph, chapter_num, content |
| `paragraphs_fts` | FTS5 index on paragraph content |
| `bible_refs` | Bible cross-references (para_id, ref_text) |
| `topics` | Topical index (topic, subtopic, book_code, page) |
| `book_index` | Book metadata (book_code, title, year, paragraph_count) |

## Usage

```bash
# ── EGW Corpus ──
egw --search "sabbath school" --limit 10      # FTS5 search
egw --search "sanctuary" --book GC             # Filter by book
egw --near "faith works" 10                    # Proximity search
egw --stats "grace"                            # Frequency by book
egw --concordance "blood"                      # Every occurrence
egw --bible "John 3:16"                        # EGW quoting this verse
egw --bible-refs GC 456                        # Bible refs in passage
egw --bible-stats                              # Most-quoted Bible books
egw --topic "health reform"                    # Topical search
egw --topics                                   # List all topics
egw --list                                     # Browse all books
egw --info GC                                  # Book metadata
egw --chapter GC 41                            # Full chapter
egw --diff GC GC88 456                         # Compare editions
egw --cite GC 456.1                            # Formatted citation
egw --person "James White"                     # Find letters mentioning

# ── KJV Bible ──
egw --kjv "John 3:16"                          # Verse lookup
egw --kjv "Romans 8:28-30"                     # Verse range
egw --kjv-search "living water" --limit 20     # FTS5 search
egw --kjv-chapter "Psalm 23"                   # Full chapter

# ── System ──
egw --update                                   # Update to latest release
egw --version                                  # Show version
```

## Requirements

- Python 3.9+
- SQLite3 (built-in)
- `requests` (for `build_kjv.py` only)
- Zero external Python dependencies for the main tool

## License

MIT — do whatever you want with it.
