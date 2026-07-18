"""Security tests for path validation and subprocess safety."""
import os
import shutil
import tempfile
import unittest


class TestInvalidSourcePath(unittest.TestCase):
    """2.1 — assert error on path traversal attempts."""

    def test_rejects_traversal(self):
        from CLI.organize import validate_source_path
        with self.assertRaises(ValueError):
            validate_source_path("../../etc/passwd")

    def test_rejects_absolute_traversal(self):
        from CLI.organize import validate_source_path
        with self.assertRaises(ValueError):
            validate_source_path("/tmp/../../etc/shadow")


class TestShellMetachar(unittest.TestCase):
    """2.2 — assert subprocess gets literal path, no shell=True."""

    def test_no_shell_true_in_copy(self):
        """organize.copy_photos must not use shell=True in subprocess calls."""
        import inspect
        from CLI.organize import copy_photos
        src = inspect.getsource(copy_photos)
        # Direct check: no shell=True in the function source
        self.assertNotIn("shell=True", src)


class TestDeleteOnHashMismatch(unittest.TestCase):
    """2.3 — assert delete blocked when SHA-256 differs."""

    def test_mismatch_aborts_delete(self):
        from CLI.organize import verify_and_delete
        tmp = tempfile.mkdtemp()
        try:
            src = os.path.join(tmp, "src.jpg")
            dst = os.path.join(tmp, "dst.jpg")
            with open(src, "wb") as f:
                f.write(b"original")
            with open(dst, "wb") as f:
                f.write(b"modified")
            # verify_and_delete should refuse to delete dst when hashes differ
            ok = verify_and_delete(src, dst, expected_sha256="deadbeef")
            self.assertFalse(ok)
            self.assertTrue(os.path.exists(dst))
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main(verbosity=2)
