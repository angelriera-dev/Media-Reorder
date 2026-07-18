"""Tests for Google Takeout sidecar parser."""
import json
import os
import shutil
import tempfile
import unittest

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import json
import shutil
import tempfile
import unittest
from CLI.sidecar import sidecar_path, parse_sidecar, get_sidecar_date



class TestSidecarPath(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_returns_json_companion(self):
        media = os.path.join(self.tmp, "photo.jpg")
        sidecar = os.path.join(self.tmp, "photo.jpg.json")
        open(media, "w").close()
        open(sidecar, "w").close()
        self.assertEqual(str(sidecar_path(media)), sidecar)

    def test_returns_none_when_missing(self):
        media = os.path.join(self.tmp, "photo.jpg")
        open(media, "w").close()
        self.assertIsNone(sidecar_path(media))


class TestParseSidecar(unittest.TestCase):

    def test_extracts_photo_taken_time(self):
        data = {"photoTakenTime": {"timestamp": "1700000000"}}
        tmp = tempfile.mkdtemp()
        try:
            path = os.path.join(tmp, "test.json")
            with open(path, "w") as f:
                json.dump(data, f)
            result = parse_sidecar(path)
            self.assertIn("photo_taken", result)
        finally:
            shutil.rmtree(tmp)

    def test_returns_none_for_invalid_json(self):
        tmp = tempfile.mkdtemp()
        try:
            path = os.path.join(tmp, "bad.json")
            with open(path, "w") as f:
                f.write("not json {{{")
            self.assertIsNone(parse_sidecar(path))
        finally:
            shutil.rmtree(tmp)

    def test_extracts_optional_fields(self):
        data = {
            "photoTakenTime": {"timestamp": "1700000000"},
            "description": "A photo",
            "title": "img001",
            "geoData": {"latitude": -34.6, "longitude": -58.4},
        }
        tmp = tempfile.mkdtemp()
        try:
            path = os.path.join(tmp, "test.json")
            with open(path, "w") as f:
                json.dump(data, f)
            result = parse_sidecar(path)
            self.assertEqual(result["description"], "A photo")
            self.assertEqual(result["title"], "img001")
            self.assertAlmostEqual(result["latitude"], -34.6)
        finally:
            shutil.rmtree(tmp)


class TestGetSidecarDate(unittest.TestCase):

    def test_returns_timestamp_string(self):
        data = {"photoTakenTime": {"timestamp": "1700000000"}}
        tmp = tempfile.mkdtemp()
        try:
            media = os.path.join(tmp, "photo.jpg")
            sidecar = os.path.join(tmp, "photo.jpg.json")
            open(media, "w").close()
            with open(sidecar, "w") as f:
                json.dump(data, f)
            result = get_sidecar_date(media)
            self.assertIsNotNone(result)
        finally:
            shutil.rmtree(tmp)

    def test_returns_none_without_sidecar(self):
        tmp = tempfile.mkdtemp()
        try:
            media = os.path.join(tmp, "photo.jpg")
            open(media, "w").close()
            self.assertIsNone(get_sidecar_date(media))
        finally:
            shutil.rmtree(tmp)


class TestRealGoogleDriveFiles(unittest.TestCase):

    def test_real_files_have_sidecars_and_dates(self):
        real_dir = os.path.join("tests", "src", "googleDrive")
        if not os.path.isdir(real_dir):
            self.skipTest(f"Directory {real_dir} not found")
        
        media_files = []
        for filename in os.listdir(real_dir):
            if filename.endswith(".jpg") or filename.endswith(".MP"):
                media_files.append(os.path.join(real_dir, filename))
        
        self.assertGreater(len(media_files), 0, "No media files found to test")
        for media_path in media_files:
            with self.subTest(media=media_path):
                sp = sidecar_path(media_path)
                self.assertIsNotNone(sp, f"Sidecar not found for {media_path}")
                self.assertTrue(os.path.isfile(sp))
                
                parsed = parse_sidecar(sp)
                self.assertIsNotNone(parsed, f"Could not parse sidecar {sp}")
                self.assertIn("photo_taken", parsed, f"No photo_taken date in parsed sidecar {sp}")
                self.assertIsNotNone(parsed["photo_taken"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
