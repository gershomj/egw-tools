#!/usr/bin/env python3
"""Build KJV Bible SQLite database with FTS5 from bible-api.com. Resumable + rate-limit aware."""
import sqlite3, time, sys, os, json, subprocess

# Auto-install requests if missing
try:
    import requests
except ImportError:
    print("Installing requests...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "requests"])
    import requests

DB = os.environ.get("KJV_DB", os.path.join(os.path.expanduser("~/.egw-tools"), "kjv.db"))
API = "https://bible-api.com/{book}+{chapter}?translation=kjv"

BOOKS = [
    ("Genesis", "GEN", 50), ("Exodus", "EXO", 40), ("Leviticus", "LEV", 27),
    ("Numbers", "NUM", 36), ("Deuteronomy", "DEU", 34), ("Joshua", "JOS", 24),
    ("Judges", "JDG", 21), ("Ruth", "RUT", 4), ("1 Samuel", "1SA", 31),
    ("2 Samuel", "2SA", 24), ("1 Kings", "1KI", 22), ("2 Kings", "2KI", 25),
    ("1 Chronicles", "1CH", 29), ("2 Chronicles", "2CH", 36), ("Ezra", "EZR", 10),
    ("Nehemiah", "NEH", 13), ("Esther", "EST", 10), ("Job", "JOB", 42),
    ("Psalms", "PSA", 150), ("Proverbs", "PRO", 31), ("Ecclesiastes", "ECC", 12),
    ("Song of Solomon", "SNG", 8), ("Isaiah", "ISA", 66), ("Jeremiah", "JER", 52),
    ("Lamentations", "LAM", 5), ("Ezekiel", "EZK", 48), ("Daniel", "DAN", 12),
    ("Hosea", "HOS", 14), ("Joel", "JOL", 3), ("Amos", "AMO", 9),
    ("Obadiah", "OBA", 1), ("Jonah", "JON", 4), ("Micah", "MIC", 7),
    ("Nahum", "NAM", 3), ("Habakkuk", "HAB", 3), ("Zephaniah", "ZEP", 3),
    ("Haggai", "HAG", 2), ("Zechariah", "ZEC", 14), ("Malachi", "MAL", 4),
    ("Matthew", "MAT", 28), ("Mark", "MRK", 16), ("Luke", "LUK", 24),
    ("John", "JHN", 21), ("Acts", "ACT", 28), ("Romans", "ROM", 16),
    ("1 Corinthians", "1CO", 16), ("2 Corinthians", "2CO", 13),
    ("Galatians", "GAL", 6), ("Ephesians", "EPH", 6), ("Philippians", "PHP", 4),
    ("Colossians", "COL", 4), ("1 Thessalonians", "1TH", 5),
    ("2 Thessalonians", "2TH", 3), ("1 Timothy", "1TI", 6),
    ("2 Timothy", "2TI", 4), ("Titus", "TIT", 3), ("Philemon", "PHM", 1),
    ("Hebrews", "HEB", 13), ("James", "JAS", 5), ("1 Peter", "1PE", 5),
    ("2 Peter", "2PE", 3), ("1 John", "1JN", 5), ("2 John", "2JN", 1),
    ("3 John", "3JN", 1), ("Jude", "JUD", 1), ("Revelation", "REV", 22),
]

# Check if DB exists and find resume point
resume_chapter = None
os.makedirs(os.path.dirname(DB), exist_ok=True)
if os.path.exists(DB):
    conn = sqlite3.connect(DB)
    done_books = conn.execute("SELECT DISTINCT book_abbr FROM verses").fetchall()
    done_set = {r[0] for r in done_books}
    if done_set:
        # Find the last completed book
        last_done = None
        for name, abbr, chs in BOOKS:
            if abbr in done_set:
                last_done = abbr
        # Find next book to start
        skip = last_done is not None
        new_books = []
        for name, abbr, chs in BOOKS:
            if skip and abbr != last_done:
                continue
            if abbr == last_done:
                skip = False
                # Check how many chapters done for this book
                max_ch = conn.execute("SELECT MAX(chapter) FROM verses WHERE book_abbr=?", (abbr,)).fetchone()[0] or 0
                max_expected = conn.execute("SELECT COUNT(DISTINCT chapter) FROM verses WHERE book_abbr=?", (abbr,)).fetchone()[0]
                if max_expected >= chs:
                    continue  # Book complete, skip
                resume_chapter = max_ch + 1
                new_books.append((name, abbr, chs))
                continue
            new_books.append((name, abbr, chs))
        BOOKS = new_books
        if resume_chapter:
            print(f"Resuming {BOOKS[0][0]} from chapter {resume_chapter}")
    conn.close()
else:
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS verses (
            id INTEGER PRIMARY KEY,
            book_name TEXT, book_abbr TEXT, chapter INTEGER, verse INTEGER,
            text TEXT, reference TEXT,
            UNIQUE(book_abbr, chapter, verse)
        )
    """)
    conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS verses_fts USING fts5(book_name, text, content=verses, content_rowid=id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_verses_ref ON verses(book_abbr, chapter, verse)")
    conn.commit()
    conn.close()

total_chapters = sum(b[2] for b in BOOKS)
done = 0
t0 = time.time()
delay = 2.0

for book_name, book_abbr, chapters in BOOKS:
    start_ch = resume_chapter if resume_chapter else 1
    resume_chapter = None
    
    for ch in range(start_ch, chapters + 1):
        done += 1
        url = API.format(book=book_name.replace(" ", "+"), chapter=ch)
        
        for attempt in range(5):
            try:
                r = requests.get(url, headers={"Accept": "application/json"}, timeout=15)
                if r.status_code == 429:
                    wait = delay * (2 ** attempt)
                    print(f"  RATE LIMITED ({book_name} {ch}), waiting {wait:.0f}s...", flush=True)
                    time.sleep(wait)
                    continue
                if r.status_code != 200:
                    print(f"  ERROR {book_name} {ch}: HTTP {r.status_code}", flush=True)
                    break
                
                conn = sqlite3.connect(DB)
                data = r.json()
                verses = data.get("verses", [])
                for v in verses:
                    text = v["text"].strip()
                    ref = f"{v['book_name']} {v['chapter']}:{v['verse']}"
                    conn.execute(
                        "INSERT OR REPLACE INTO verses(book_name, book_abbr, chapter, verse, text, reference) VALUES(?,?,?,?,?,?)",
                        (v["book_name"], book_abbr, v["chapter"], v["verse"], text, ref)
                    )
                conn.execute("INSERT INTO verses_fts(verses_fts) VALUES('rebuild')")
                conn.commit()
                conn.close()
                break
                
            except Exception as e:
                if attempt < 4:
                    time.sleep(delay * (2 ** attempt))
                else:
                    print(f"  FAIL {book_name} {ch}: {e}", flush=True)
        
        elapsed = time.time() - t0
        rate = done / elapsed if elapsed > 0 else 0
        pct = done / total_chapters * 100
        eta = (total_chapters - done) / rate / 60 if rate > 0 else 0
        print(f"  [{pct:.0f}%] {book_name} {ch} ({len(verses)}v) | {done}/{total_chapters} ch | {rate:.1f} ch/s | ETA {eta:.0f}m", flush=True)
        
        time.sleep(delay)

# Stats
conn = sqlite3.connect(DB)
count = conn.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
olds = conn.execute("SELECT COUNT(*) FROM verses WHERE book_abbr IN ('GEN','EXO','LEV','NUM','DEU','JOS','JDG','RUT','1SA','2SA','1KI','2KI','1CH','2CH','EZR','NEH','EST','JOB','PSA','PRO','ECC','SNG','ISA','JER','LAM','EZK','DAN','HOS','JOL','AMO','OBA','JON','MIC','NAM','HAB','ZEP','HAG','ZEC','MAL')").fetchone()[0]
news = count - olds
conn.close()

size = os.path.getsize(DB) / 1e6
print(f"\nDONE. {count:,} verses ({olds:,} OT, {news:,} NT) in {(time.time()-t0)/60:.1f}m")
print(f"Database: {size:.1f} MB — {DB}")
