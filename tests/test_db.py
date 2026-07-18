"""Tests for database layer."""
import os
import shutil
import tempfile
import unittest

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import shutil
import tempfile
import unittest
from CLI.db import (
    get_db, record_copy, get_cached_metadata, cache_metadata,
    add_tag, tag_file, compute_sha256,
)



class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp, "test.db")
        self.conn = get_db(self.db_path)

    def tearDown(self):
        self.conn.close()
        shutil.rmtree(self.tmp)

    def test_schema_creates_tables(self):
        tables = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        names = {t[0] for t in tables}
        self.assertIn("copy_history", names)
        self.assertIn("metadata_cache", names)
        self.assertIn("tags", names)
        self.assertIn("file_tags", names)

    def test_record_copy(self):
        record_copy(self.conn, "/src/a.jpg", "/dst/a.jpg", 1024, "abc123")
        row = self.conn.execute("SELECT * FROM copy_history").fetchone()
        self.assertEqual(row[1], "/src/a.jpg")
        self.assertEqual(row[2], "/dst/a.jpg")
        self.assertEqual(row[3], 1024)
        self.assertEqual(row[4], "abc123")

    def test_cache_metadata_roundtrip(self):
        cache_metadata(self.conn, "/img.jpg", 1234.0, exif_date="2024:01:01")
        row = get_cached_metadata(self.conn, "/img.jpg", 1234.0)
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "2024:01:01")

    def test_cache_metadata_miss(self):
        row = get_cached_metadata(self.conn, "/nope.jpg", 999.0)
        self.assertIsNone(row)

    def test_add_tag_and_tag_file(self):
        tag_id = add_tag(self.conn, "vacation")
        self.assertIsInstance(tag_id, int)
        tag_file(self.conn, "/img.jpg", tag_id)
        rows = self.conn.execute(
            "SELECT * FROM file_tags WHERE file_path = '/img.jpg'"
        ).fetchall()
        self.assertEqual(len(rows), 1)

    def test_compute_sha256(self):
        path = os.path.join(self.tmp, "data.bin")
        with open(path, "wb") as f:
            f.write(b"hello world")
        sha = compute_sha256(path)
        # Known SHA-256 for "hello world"
        self.assertEqual(
            sha, "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
