import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
for module_name in ("iso_preflight", "xdvdfs_root"):
    module_path = ROOT / "tools" / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    import sys
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    if module_name == "xdvdfs_root":
        xdvdfs_root = module


class XdvdfsRootTests(unittest.TestCase):
    def make_image(self, *, entry_name=b"default.xex", bad_name_length=False, bad_extent=False):
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.close()
        path = Path(temp.name)
        partition = 0
        descriptor_offset = 32 * 2048
        root_offset = 33 * 2048
        root_bytes = 128
        image_size = 34 * 2048
        with path.open("wb") as stream:
            stream.truncate(image_size)
            descriptor = bytearray(2048)
            magic = b"MICROSOFT*XBOX*MEDIA"
            descriptor[:len(magic)] = magic
            descriptor[-len(magic):] = magic
            struct.pack_into("<II", descriptor, 20, 33, root_bytes)
            stream.seek(descriptor_offset)
            stream.write(descriptor)
            entry = bytearray(14 + len(entry_name))
            struct.pack_into("<HHII", entry, 0, 0xFFFF, 0xFFFF, 0xFFFFFFFF if bad_extent else 33, 4)
            entry[12] = 0
            entry[13] = 255 if bad_name_length else len(entry_name)
            entry[14:] = entry_name
            entry.extend(b"\0" * ((-len(entry)) % 4))
            stream.seek(root_offset)
            stream.write(entry)
        self.addCleanup(path.unlink, missing_ok=True)
        return path

    def test_lists_root_and_finds_default_xex_without_claiming_identity(self):
        result = xdvdfs_root.list_root(self.make_image())
        self.assertTrue(result["default_xex_present"])
        self.assertEqual(result["root_entry_count"], 1)
        self.assertFalse(result["revision_verified"])

    def test_case_insensitive_default_xex(self):
        self.assertTrue(xdvdfs_root.list_root(self.make_image(entry_name=b"DEFAULT.XEX"))["default_xex_present"])

    def test_rejects_name_length_past_directory(self):
        with self.assertRaises(xdvdfs_root.DirectoryError):
            xdvdfs_root.list_root(self.make_image(bad_name_length=True))

    def test_rejects_file_extent_outside_image(self):
        with self.assertRaises(xdvdfs_root.DirectoryError):
            xdvdfs_root.list_root(self.make_image(bad_extent=True))


if __name__ == "__main__":
    unittest.main()
