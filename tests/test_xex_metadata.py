import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "tools" / "xex_metadata.py"
spec = importlib.util.spec_from_file_location("xex_metadata", MODULE_PATH)
xex_metadata = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(xex_metadata)


class XexMetadataTests(unittest.TestCase):
    def make_xex(self, *, magic=b"XEX2", include_execution=True, bad_offset=False):
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.close()
        path = Path(temp.name)
        header_count = 1 if include_execution else 0
        execution_offset = 0x40 if not bad_offset else 0xFFFFFFF0
        with path.open("wb") as stream:
            header = bytearray(0x18)
            header[:4] = magic
            struct.pack_into(">I", header, 20, header_count)
            stream.write(header)
            if include_execution:
                stream.write(struct.pack(">II", 0x00040006, execution_offset))
            stream.write(b"\0" * max(0, execution_offset - stream.tell()))
            if not bad_offset:
                stream.write(struct.pack(">IIII", 0x12345678, 1, 1, 0x4D5307FC))
                stream.write(bytes([1, 2, 1, 1]))
                stream.write(struct.pack(">I", 0xAABBCCDD))
        self.addCleanup(path.unlink, missing_ok=True)
        return path

    def test_reads_execution_metadata_without_claiming_revision(self):
        result = xex_metadata.inspect_xex(self.make_xex())
        self.assertEqual(result["title_id"], "4D5307FC")
        self.assertEqual(result["media_id"], "12345678")
        self.assertFalse(result["revision_verified"])

    def test_rejects_wrong_magic(self):
        with self.assertRaises(xex_metadata.XexError):
            xex_metadata.inspect_xex(self.make_xex(magic=b"NOPE"))

    def test_rejects_missing_execution_header(self):
        with self.assertRaises(xex_metadata.XexError):
            xex_metadata.inspect_xex(self.make_xex(include_execution=False))

    def test_rejects_out_of_bounds_execution_pointer(self):
        with self.assertRaises(xex_metadata.XexError):
            xex_metadata.inspect_xex(self.make_xex(bad_offset=True))

    def test_rejects_tiny_file(self):
        with tempfile.NamedTemporaryFile() as stream:
            stream.write(b"XEX")
            stream.flush()
            with self.assertRaises(xex_metadata.XexError):
                xex_metadata.inspect_xex(stream.name)


if __name__ == "__main__":
    unittest.main()
