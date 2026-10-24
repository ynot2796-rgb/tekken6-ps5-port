import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "patch_radv_linker.py"
SPEC = importlib.util.spec_from_file_location("patch_radv_linker", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PatchRadvLinkerTests(unittest.TestCase):
    def apply(self, source: str) -> tuple[str, bool]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "build-radv-title.sh"
            path.write_text(source, encoding="utf-8")
            changed = MODULE.patch_linker_script(path)
            return path.read_text(encoding="utf-8"), changed

    def test_patches_exact_link_command(self):
        source = 'before\n' + MODULE.NEEDLE + ' "$@"\nafter\n'
        result, changed = self.apply(source)
        self.assertTrue(changed)
        self.assertEqual(result.count(MODULE.REPLACEMENT), 1)
        self.assertNotIn(MODULE.NEEDLE, result)

    def test_already_patched_is_idempotent(self):
        result, changed = self.apply(MODULE.REPLACEMENT + "\n")
        self.assertFalse(changed)
        self.assertEqual(result, MODULE.REPLACEMENT + "\n")

    def test_fails_closed_if_upstream_command_drifts(self):
        with self.assertRaises(ValueError):
            self.apply('prospero-lld --unexpected-new-layout\n')

    def test_fails_closed_if_command_is_duplicated(self):
        with self.assertRaises(ValueError):
            self.apply(MODULE.NEEDLE + "\n" + MODULE.NEEDLE + "\n")


if __name__ == "__main__":
    unittest.main()
