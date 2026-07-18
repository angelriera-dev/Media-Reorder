import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import unittest
import tempfile
import shutil
from CLI.db import get_db, cache_metadata
from CLI.dates import get_photo_date
import CLI.dates as dates_module

class TestDateExtractionRefactoring(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp, "test.db")
        self.conn = get_db(self.db_path)
        
        # Create a dummy file
        self.img_path = os.path.join(self.tmp, "test.jpg")
        with open(self.img_path, "wb") as f:
            f.write(b"dummy image data")
        self.mtime = os.path.getmtime(self.img_path)

    def tearDown(self):
        self.conn.close()
        shutil.rmtree(self.tmp)

    def test_get_earliest_date(self):
        # 1. Populate cache with a "newer" date
        cache_metadata(self.conn, self.img_path, self.mtime, exif_date="2025:01:01")
        
        # 2. Simulate "earlier" date from another source (e.g., sidecar)
        # Note: We need to mock get_sidecar_date because it's imported in dates.py
        original_sidecar = dates_module.get_sidecar_date
        dates_module.get_sidecar_date = lambda path: "2020-01-01"
        
        try:
            # 3. Expectation: The function should return 2020-01-01 (the earliest)
            result = get_photo_date(self.img_path, conn=self.conn)
            
            self.assertIsNotNone(result)
            # result is (*date, source_tag)
            # date is (year, month, day)
            year, month, day, source = result
            self.assertEqual((year, month, day), (2020, 1, 1))
            self.assertEqual(source, "min_of_all")
        finally:
            dates_module.get_sidecar_date = original_sidecar

if __name__ == "__main__":
    unittest.main(verbosity=2)
