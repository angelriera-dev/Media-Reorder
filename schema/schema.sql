-- reorder database schema (source of truth)
-- Execute via db.py at runtime to create/reorder.db

CREATE TABLE IF NOT EXISTS copy_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_path TEXT NOT NULL,
    dest_path TEXT NOT NULL,
    file_size INTEGER,
    sha256 TEXT,
    copied_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS metadata_cache (
    file_path TEXT NOT NULL,
    mtime REAL NOT NULL,
    exif_date TEXT,
    sidecar_date TEXT,
    raw_json TEXT,
    cached_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (file_path, mtime)
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS file_tags (
    file_path TEXT NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (file_path, tag_id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
