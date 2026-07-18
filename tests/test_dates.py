"""Tests for dates module helpers."""
import os
import shutil
import tempfile
import unittest

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import unittest
from CLI.dates import _parse_date_string, _is_reasonable_date, format_date, batch_exiftool



class TestParseDateString(unittest.TestCase):

    def test_colon_format(self):
        self.assertEqual(_parse_date_string("2024:03:15 14:30:00"), (2024, 3, 15))

    def test_dash_format(self):
        self.assertEqual(_parse_date_string("2024-03-15"), (2024, 3, 15))

    def test_slash_format(self):
        self.assertEqual(_parse_date_string("2024/03/15"), (2024, 3, 15))

    def test_no_match(self):
        self.assertIsNone(_parse_date_string("no date here"))


class TestIsReasonableDate(unittest.TestCase):

    def test_valid(self):
        self.assertTrue(_is_reasonable_date((2024, 6, 15)))

    def test_future_rejected(self):
        self.assertFalse(_is_reasonable_date((2099, 1, 1)))

    def test_epoch_rejected(self):
        self.assertFalse(_is_reasonable_date((1970, 1, 1)))

    def test_old_rejected(self):
        self.assertFalse(_is_reasonable_date((1980, 1, 1)))


class TestFormatDate(unittest.TestCase):

    def test_returns_tuple(self):
        day_str, month_name = format_date(2024, 6, 15)
        self.assertIsNotNone(day_str)
        self.assertEqual(month_name, "Jun")

    def test_invalid_returns_none(self):
        self.assertEqual(format_date(2024, 13, 1), (None, None))


class TestBatchExiftool(unittest.TestCase):

    def test_returns_list(self):
        result = batch_exiftool("/nonexistent")
        self.assertIsInstance(result, list)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
