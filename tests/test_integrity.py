"""
Tests de integridad para reorder.
Cubre los 3 bugs encontrados + verificación post-copia.
Requiere: Python stdlib únicamente (no pytest, no fixtures extra).
"""
import os
import sys
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reorder.organize import _safe_target_path, copy_photos, verify_copy
from reorder.search import find_images


# ──────────────────────────────────────────────────────────────
# Bug 1 — Deduplicación segura
# ──────────────────────────────────────────────────────────────
class TestSafeTargetPath(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_no_collision_returns_original(self):
        path = _safe_target_path(self.tmp, "foto.jpg")
        self.assertEqual(path, os.path.join(self.tmp, "foto.jpg"))

    def test_single_collision_returns_dup1(self):
        # Crear el archivo original para simular colisión
        open(os.path.join(self.tmp, "foto.jpg"), "w").close()
        path = _safe_target_path(self.tmp, "foto.jpg")
        self.assertEqual(path, os.path.join(self.tmp, "foto_dup1.jpg"))

    def test_multiple_collisions_increments_safely(self):
        # Crear foto.jpg, foto_dup1.jpg, foto_dup2.jpg
        for name in ["foto.jpg", "foto_dup1.jpg", "foto_dup2.jpg"]:
            open(os.path.join(self.tmp, name), "w").close()
        path = _safe_target_path(self.tmp, "foto.jpg")
        self.assertEqual(path, os.path.join(self.tmp, "foto_dup3.jpg"))
        # Verificar que el path devuelto NO existe todavía
        self.assertFalse(os.path.exists(path))


# ──────────────────────────────────────────────────────────────
# Bug 2 — Exclusión de output_dir del escaneo
# ──────────────────────────────────────────────────────────────
class TestFindImagesExcludesOutputDir(unittest.TestCase):

    def setUp(self):
        self.src = tempfile.mkdtemp()
        self.out = os.path.join(self.src, "order")
        os.makedirs(self.out)
        # Foto en src raíz
        open(os.path.join(self.src, "real.jpg"), "w").close()
        # Foto dentro del directorio de salida (no debe aparecer)
        open(os.path.join(self.out, "already_copied.jpg"), "w").close()

    def tearDown(self):
        shutil.rmtree(self.src)

    def test_output_dir_is_excluded(self):
        found = list(find_images(self.src, exclude_dir=os.path.realpath(self.out)))
        names = [os.path.basename(p) for p in found]
        self.assertIn("real.jpg", names)
        self.assertNotIn("already_copied.jpg", names)

    def test_without_exclusion_finds_both(self):
        found = list(find_images(self.src))
        names = [os.path.basename(p) for p in found]
        self.assertIn("real.jpg", names)
        self.assertIn("already_copied.jpg", names)


# ──────────────────────────────────────────────────────────────
# Bug 3 — _is_reasonable_date en estrategia 1 de exiftool
# ──────────────────────────────────────────────────────────────
from reorder.dates import _parse_date_string, _is_reasonable_date

class TestReasonableDateFilter(unittest.TestCase):

    def test_zero_date_is_rejected(self):
        date = _parse_date_string("0000:00:00 00:00:00")
        self.assertIsNotNone(date)               # sí se parsea
        self.assertFalse(_is_reasonable_date(date))  # pero se rechaza

    def test_epoch_is_rejected(self):
        self.assertFalse(_is_reasonable_date((1970, 1, 1)))

    def test_future_date_is_rejected(self):
        self.assertFalse(_is_reasonable_date((2099, 1, 1)))

    def test_valid_date_is_accepted(self):
        self.assertTrue(_is_reasonable_date((2024, 6, 15)))

    def test_invalid_month_is_rejected(self):
        self.assertFalse(_is_reasonable_date((2024, 13, 1)))

    def test_invalid_day_is_rejected(self):
        self.assertFalse(_is_reasonable_date((2024, 1, 32)))


# ──────────────────────────────────────────────────────────────
# Verificación post-copia
# ──────────────────────────────────────────────────────────────
class TestVerifyCopy(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _make_file(self, name, content=b"data"):
        path = os.path.join(self.tmp, name)
        with open(path, "wb") as f:
            f.write(content)
        return path

    def test_all_ok(self):
        src = self._make_file("src.jpg", b"hello")
        dst = self._make_file("dst.jpg", b"hello")
        ok, missing, mismatch = verify_copy({src: dst})
        self.assertTrue(ok)
        self.assertEqual(missing, [])
        self.assertEqual(mismatch, [])

    def test_missing_destination(self):
        src = self._make_file("src.jpg", b"hello")
        dst = os.path.join(self.tmp, "nonexistent.jpg")
        ok, missing, mismatch = verify_copy({src: dst})
        self.assertFalse(ok)
        self.assertIn(dst, missing)

    def test_size_mismatch(self):
        src = self._make_file("src.jpg", b"hello")
        dst = self._make_file("dst.jpg", b"he")   # tamaño distinto
        ok, missing, mismatch = verify_copy({src: dst})
        self.assertFalse(ok)
        self.assertEqual(len(mismatch), 1)
        self.assertEqual(mismatch[0][1], 5)   # src_size
        self.assertEqual(mismatch[0][3], 2)   # dst_size

    def test_empty_copy_dict_is_ok(self):
        ok, missing, mismatch = verify_copy({})
        self.assertTrue(ok)


class TestRealCopyPhotos(unittest.TestCase):

    def test_copy_real_photos_to_tests_reorder(self):
        src_dir = os.path.join("tests", "src")
        dst_dir = os.path.join("tests", "reorder")

        # Clean destination directory to ensure clean run
        if os.path.exists(dst_dir):
            shutil.rmtree(dst_dir)

        from reorder.db import get_db
        db_path = os.path.join("tests", "reorder_test.db")
        if os.path.exists(db_path):
            os.remove(db_path)

        conn = get_db(db_path)
        try:
            copied = copy_photos(src_dir, dst_dir, conn=conn)
            self.assertGreater(len(copied), 0, "Should have copied some media files")

            # Verify integrity
            ok, missing, mismatch = verify_copy(copied)
            self.assertTrue(ok, f"Verification failed: missing={missing}, mismatch={mismatch}")
        finally:
            conn.close()
            if os.path.exists(db_path):
                os.remove(db_path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
