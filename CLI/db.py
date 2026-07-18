"""SQLite database layer for reorder.

Reads schema/schema.sql to create/reorder.db. Provides CRUD helpers.
"""
import hashlib
import sqlite3
from pathlib import Path

# Removed _DB_PATH, it is now the responsibility of the caller to provide the path.
_SCHEMA_SQL = Path(__file__).resolve().parent.parent / "schema" / "schema.sql"


def get_db(db_path: str | Path) -> sqlite3.Connection:
    """Return a connection to the specified db_path, initializing schema if needed."""
    path = Path(db_path)
    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA journal_mode=WAL")
    _init_schema(conn)
    return conn


def _init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(_SCHEMA_SQL.read_text())


def record_copy(conn: sqlite3.Connection, source: str, dest: str,
                file_size: int | None = None, sha256: str | None = None) -> None:
    conn.execute(
        "INSERT INTO copy_history (source_path, dest_path, file_size, sha256) "
        "VALUES (?, ?, ?, ?)",
        (source, dest, file_size, sha256),
    )
    conn.commit()


def get_cached_metadata(conn: sqlite3.Connection, file_path: str, mtime: float):
    row = conn.execute(
        "SELECT exif_date, sidecar_date, raw_json FROM metadata_cache "
        "WHERE file_path = ? AND mtime = ?",
        (file_path, mtime),
    ).fetchone()
    return row  # (exif_date, sidecar_date, raw_json) or None


def cache_metadata(conn: sqlite3.Connection, file_path: str, mtime: float,
                   exif_date: str | None = None, sidecar_date: str | None = None,
                   raw_json: str | None = None) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO metadata_cache "
        "(file_path, mtime, exif_date, sidecar_date, raw_json) "
        "VALUES (?, ?, ?, ?, ?)",
        (file_path, mtime, exif_date, sidecar_date, raw_json),
    )
    conn.commit()


def add_tag(conn: sqlite3.Connection, name: str) -> int:
    cur = conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (name,))
    if cur.rowcount == 0:
        row = conn.execute("SELECT id FROM tags WHERE name = ?", (name,)).fetchone()
        return row[0]
    conn.commit()
    return cur.lastrowid


def tag_file(conn: sqlite3.Connection, file_path: str, tag_id: int) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO file_tags (file_path, tag_id) VALUES (?, ?)",
        (file_path, tag_id),
    )
    conn.commit()


def compute_sha256(file_path: str | Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
