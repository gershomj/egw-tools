#!/usr/bin/env python3
"""Build EGW corpus database from EGW Writings CDN.
Downloads EPUBs, extracts text, builds SQLite FTS5 database.
Resumable — tracks progress in a state file."""

import sqlite3, os, sys, time, json, zipfile, re
from html.parser import HTMLParser
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from pathlib import Path

# ── Config ─────────────────────────────────────────────
OUTPUT_DB = Path("/root/.hermes/egw-corpus.db").resolve()
STATE_FILE = Path("/tmp/egw-build-state.json")
WORK_DIR = Path("/tmp/egw-build")
CDN_EPUB = "https://media2.egwwritings.org/epub/en_{code}.epub"
CDN_PDF  = "https://media2.egwwritings.org/pdf/en_{code}.pdf"

# All known book codes — sorted by importance/popularity
BOOK_CODES = [
    # Major works
    "GC", "DA", "PP", "PK", "SC", "EW", "AA", "MH", "MB", "Ed",
    "COL", "SR", "GW", "TM", "LP", "LS", "CT", "AH", "CD", "CG",
    "CM", "Ev", "FLB", "LDE", "Mar", "MM", "MYP", "OHC", "RC",
    "SD", "Te", "TMK", "LHU", "AG", "CSA", "DG", "ChS", "CSW",
    # Testimonies (1-9)
    "1T", "2T", "3T", "4T", "5T", "6T", "7T", "8T", "9T",
    # Selected Messages (1-3)
    "1SM", "2SM", "3SM",
    # Spiritual Gifts (1-4)
    "1SG", "2SG", "3SG", "4SG",
    # Manuscript Releases (1-21)
    *[f"{i}MR" for i in range(1, 22)],
]

class TextExtractor(HTMLParser):
    """Extract clean text from EPUB HTML, preserving paragraph breaks."""
    def __init__(self):
        super().__init__()
        self.paragraphs = []
        self.current = []
        self.skip = 0
    
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'head'):
            self.skip += 1
        elif tag in ('p', 'br', 'div', 'h1', 'h2', 'h3', 'h4', 'li', 'tr', 'blockquote'):
            if self.current:
                text = ' '.join(self.current).strip()
                if text:
                    self.paragraphs.append(text)
                self.current = []
    
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'head'):
            self.skip = max(0, self.skip - 1)
    
    def handle_data(self, data):
        if self.skip == 0:
            self.current.append(data)

def download_file(url, dest, timeout=120):
    """Download a file with progress indication."""
    try:
        req = Request(url, headers={"User-Agent": "egw-corpus-builder/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            total = int(resp.headers.get('content-length', 0))
            with open(dest, 'wb') as f:
                downloaded = 0
                while True:
                    chunk = resp.read(8192 * 16)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = downloaded / total * 100
                        mb = downloaded / 1e6
                        total_mb = total / 1e6
                        print(f"\r  {pct:5.1f}%  {mb:5.0f}/{total_mb:.0f} MB", end='', flush=True)
        print()
        return True
    except HTTPError as e:
        print(f"  HTTP {e.code} — skipping")
        return False
    except Exception as e:
        print(f"  Failed: {e}")
        return False

def extract_epub(epub_path):
    """Extract paragraphs from an EPUB file."""
    paragraphs = []
    try:
        with zipfile.ZipFile(epub_path) as z:
            html_files = sorted([
                f for f in z.namelist()
                if f.endswith(('.html', '.xhtml', '.htm'))
                and not f.startswith('__')
            ])
            for html_file in html_files:
                extractor = TextExtractor()
                try:
                    extractor.feed(z.read(html_file).decode('utf-8', errors='replace'))
                    paragraphs.extend(extractor.paragraphs)
                except Exception:
                    continue
    except Exception as e:
        print(f"  ZIP error: {e}")
        return []
    return paragraphs

def init_db(db_path):
    """Initialize SQLite database with FTS5."""
    db = sqlite3.connect(str(db_path))
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=NORMAL")
    
    db.executescript("""
        CREATE TABLE IF NOT EXISTS works (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            title TEXT,
            year INTEGER,
            paragraph_count INTEGER DEFAULT 0
        );
        
        CREATE TABLE IF NOT EXISTS paragraphs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_id INTEGER NOT NULL REFERENCES works(id),
            para_num INTEGER NOT NULL,
            chapter TEXT,
            content TEXT NOT NULL
        );
        
        CREATE VIRTUAL TABLE IF NOT EXISTS paragraphs_fts 
        USING fts5(content, content=paragraphs, content_rowid=id);
        
        CREATE INDEX IF NOT EXISTS idx_para_work ON paragraphs(work_id);
        CREATE INDEX IF NOT EXISTS idx_works_code ON works(code);
    """)
    db.commit()
    return db

def build():
    """Main build function."""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load or init state
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.open().read())
        completed = set(state.get('completed', []))
        failed = set(state.get('failed', []))
    else:
        state = {'completed': [], 'failed': []}
        completed = set()
        failed = set()
    
    db = init_db(OUTPUT_DB)
    
    total = len(BOOK_CODES)
    success_count = len(completed)
    
    print(f"\n{'='*60}")
    print(f"EGW Corpus Builder")
    print(f"Output: {OUTPUT_DB}")
    print(f"Books: {total} total | {success_count} done | {len(failed)} failed")
    print(f"{'='*60}\n")
    
    for i, code in enumerate(BOOK_CODES):
        if code in completed:
            continue
        
        print(f"[{i+1}/{total}] {code} ", end='', flush=True)
        
        # Try EPUB first
        epub_url = CDN_EPUB.format(code=code)
        epub_path = WORK_DIR / f"{code}.epub"
        
        downloaded = False
        if epub_path.exists():
            print("(cached EPUB) ", end='')
            downloaded = True
        else:
            downloaded = download_file(epub_url, epub_path, timeout=180)
        
        if downloaded:
            print("  Extracting...", end='', flush=True)
            paragraphs = extract_epub(epub_path)
            if paragraphs:
                # Insert into database
                db.execute(
                    "INSERT OR REPLACE INTO works (code, title, year, paragraph_count) VALUES (?, ?, ?, ?)",
                    (code, code, None, len(paragraphs))
                )
                work_id = db.execute("SELECT id FROM works WHERE code=?", (code,)).fetchone()[0]
                
                for j, para in enumerate(paragraphs):
                    db.execute(
                        "INSERT INTO paragraphs (work_id, para_num, chapter, content) VALUES (?, ?, ?, ?)",
                        (work_id, j+1, None, para)
                    )
                
                db.commit()
                # Rebuild FTS index
                db.execute("INSERT INTO paragraphs_fts(paragraphs_fts) VALUES('rebuild')")
                db.commit()
                
                completed.add(code)
                success_count += 1
                print(f" ✓ {len(paragraphs):,} paragraphs")
            else:
                failed.add(code)
                print(" ✗ no content extracted")
        else:
            failed.add(code)
        
        # Save state every 5 books
        if (i + 1) % 5 == 0:
            state = {'completed': list(completed), 'failed': list(failed)}
            json.dump(state, STATE_FILE.open('w'))
            db.commit()
        
        # Small delay between books
        time.sleep(0.5)
    
    # Final state save
    state = {'completed': list(completed), 'failed': list(failed)}
    json.dump(state, STATE_FILE.open('w'))
    
    # Final stats
    db.commit()
    total_paras = db.execute("SELECT COUNT(*) FROM paragraphs").fetchone()[0]
    total_works = db.execute("SELECT COUNT(*) FROM works").fetchone()[0]
    
    print(f"\n{'='*60}")
    print(f"BUILD COMPLETE")
    print(f"Works: {total_works} | Paragraphs: {total_paras:,}")
    print(f"Succeeded: {len(completed)} | Failed: {len(failed)}")
    if failed:
        print(f"Failed codes: {', '.join(sorted(failed))}")
    print(f"Database: {OUTPUT_DB} ({os.path.getsize(OUTPUT_DB)/1e9:.1f} GB)")
    print(f"{'='*60}")
    
    db.close()

if __name__ == "__main__":
    build()
