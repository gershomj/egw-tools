# egw — EGW Writings + KJV Bible Search

One command. Zero config. Works on Linux, macOS, and Windows.

```
egw --kjv "John 3:16"          # KJV verse
egw --search "sanctuary"       # EGW corpus search
egw --bible "Revelation 13"    # EGW citing verse
```

## Install

### Linux / macOS
```bash
curl -sSL https://raw.githubusercontent.com/gershomj/egw-tools/main/install.sh | bash
```

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/gershomj/egw-tools/main/install.ps1 | iex
```

That's it. The KJV Bible builds automatically in the background on first use (~40 minutes). You can use the tool immediately.

## What it does

| Command | Result |
|---|---|
| `egw --kjv "John 3:16"` | Look up a KJV verse |
| `egw --kjv "Romans 8:28-30"` | Verse range |
| `egw --kjv-search "living water"` | FTS5 search KJV |
| `egw --kjv-chapter "Psalm 23"` | Full chapter |
| `egw --search "sabbath school"` | FTS5 search EGW |
| `egw --search "prayer" --book SC` | Filter by book |
| `egw --bible "John 3:16"` | Find EGW citing verse |
| `egw --bible-stats` | Most-quoted Bible books |
| `egw --stats "grace"` | Term frequency |
| `egw --near "faith works" 10` | Proximity search |
| `egw --topic "sanctuary"` | Topical index |
| `egw --chapter GC 41` | Full chapter |
| `egw --cite GC 456.1` | Formatted citation |
| `egw --person "James White"` | Letters mentioning |
| `egw --list` | Browse all books |
| `egw GC 456.1` | Exact paragraph |
| `egw --update` | Update to latest |
| `egw --version` | Show version |
| `egw --kjv-status` | KJV build progress |

## Requirements

- Python 3.9+ (auto-detected by installer)
- Nothing else. No pip packages. No Docker. No config files.

Everything lives in `~/.egw-tools/`. The installer puts `egw` in your PATH.

## EGW Database

KJV works out of the box. For EGW search, place an `egw-corpus.db` in `~/.egw-tools/`.

The expected schema:
- `paragraphs` — book_code, page, paragraph, content, chapter_num
- `paragraphs_fts` — FTS5 index
- `bible_refs` — cross-references
- `topics` — topical index
- `book_index` — book metadata

## Updating

```bash
egw --update
```

Checks GitHub for latest release, downloads, replaces itself. One command.

## License

MIT
