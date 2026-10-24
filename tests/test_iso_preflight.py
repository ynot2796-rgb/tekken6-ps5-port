import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "tools" / "iso_preflight.py"
spec = importlib.util.spec_from_file_location("iso_preflight", MODULE_PATH)
iso_preflight = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(iso_preflight)


class IsoPreflightTests(unittest.TestCase):
    def make_image(self, *, valid=True, partition=0):
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.close()
        path = Path(temp.name)
        size = partition + 34 * 2048
        with path.open("wb") as f:
            f.truncate(size)
            if valid:
                descriptor = bytearray(2048)
                magic = b"MICROSOFT*XBOX*MEDIA"
                descriptor[:len(magic)] = magic
                descriptor[-len(magic):] = magic
                struct.pack_into("<II", descriptor, 20, 33, 64)
                f.seek(partition + 32 * 2048)
                f.write(descriptor)
        self.addCleanup(path.unlink, missing_ok=True)
        return path

    def test_recognizes_valid_xdvdfs_descriptor(self):
        path = self.make_image()
        result = iso_preflight.inspect_image(path)
        self.assertTrue(result["valid_xdvdfs_structure"])
        self.assertFalse(result["game_identity_verified"])
        self.assertEqual(result["root_directory_offset"], 33 * 2048)

    def test_recognizes_nonzero_partition_candidate(self):
        partition = 0x02080000
        path = self.make_image(partition=partition)
        result = iso_preflight.inspect_image(path)
        self.assertEqual(result["partition_offset"], partition)

    def test_rejects_random_or_corrupt_image(self):
        path = self.make_image(valid=False)
        with self.assertRaises(iso_preflight.ImageError):
            iso_preflight.inspect_image(path)

    def test_rejects_tiny_file(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(b"not an iso")
            f.flush()
            with self.assertRaises(iso_preflight.ImageError):
                iso_preflight.inspect_image(f.name)

    def test_rejects_directory_path(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(iso_preflight.ImageError):
                iso_preflight.inspect_image(d)


if __name__ == "__main__":
    unittest.main()
