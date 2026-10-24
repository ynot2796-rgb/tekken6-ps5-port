import importlib.util
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
for module_name in ("iso_preflight", "xdvdfs_root", "xex_metadata", "game_image_report"):
    module_path = ROOT / "tools" / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    if module_name == "game_image_report":
        game_image_report = module


class GameImageReportTests(unittest.TestCase):
    def make_image(self, *, include_xex=True, corrupt_xex=False):
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.close()
        path = Path(temp.name)
        descriptor_offset = 32 * 2048
        root_offset = 33 * 2048
        xex_offset = 34 * 2048
        image_size = 35 * 2048
        xex = bytearray(0x100)
        xex[:4] = b"BAD!" if corrupt_xex else b"XEX2"
        struct.pack_into(">I", xex, 20, 1)
        struct.pack_into(">II", xex, 24, 0x00040006, 0x40)
        struct.pack_into(">IIII", xex, 0x40, 0x12345678, 0x00010000,
                         0x00010000, 0x58410B00)
        xex[0x50:0x54] = bytes((1, 0, 1, 1))
        struct.pack_into(">I", xex, 0x54, 0x12345678)

        with path.open("wb") as stream:
            stream.truncate(image_size)
            descriptor = bytearray(2048)
            magic = b"MICROSOFT*XBOX*MEDIA"
            descriptor[:len(magic)] = magic
            descriptor[-len(magic):] = magic
            struct.pack_into("<II", descriptor, 20, 33, 128)
            stream.seek(descriptor_offset)
            stream.write(descriptor)
            if include_xex:
                name = b"default.xex"
                entry = bytearray(14 + len(name))
                struct.pack_into("<HHII", entry, 0, 0xFFFF, 0xFFFF, 34, len(xex))
                entry[12] = 0
                entry[13] = len(name)
                entry[14:] = name
                entry.extend(b"\0" * ((-len(entry)) % 4))
                stream.seek(root_offset)
                stream.write(entry)
                stream.seek(xex_offset)
                stream.write(xex)
        self.addCleanup(path.unlink, missing_ok=True)
        return path

    def test_reports_xex_metadata_without_claiming_game_identity(self):
        result = game_image_report.inspect_game_image(self.make_image())
        self.assertTrue(result["default_xex_present"])
        self.assertEqual(result["xex_metadata"]["title_id"], "58410B00")
        self.assertFalse(result["game_identity_verified"])
        self.assertFalse(result["revision_verified"])
        self.assertFalse(result["import_ready"])

    def test_rejects_image_without_root_default_xex(self):
        with self.assertRaises(game_image_report.GameImageError):
            game_image_report.inspect_game_image(self.make_image(include_xex=False))

    def test_rejects_invalid_xex_header(self):
        with self.assertRaises(game_image_report.XexError):
            game_image_report.inspect_game_image(self.make_image(corrupt_xex=True))


if __name__ == "__main__":
    unittest.main()
