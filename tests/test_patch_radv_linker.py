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
            path = Path(directory) / "link-title.sh"
            path.write_text(source, encoding="utf-8")
            changed = MODULE.patch_linker_script(path)
            return path.read_text(encoding="utf-8"), changed

    def test_patches_smoke_title_sdk_root_command(self):
        result, changed = self.apply(MODULE.NEEDLES[0] + "\n")
        self.assertTrue(changed)
        self.assertEqual(result.count(MODULE.REPLACEMENTS[0]), 1)
        self.assertNotIn(MODULE.NEEDLES[0], result)

    def test_patches_template_title_sdk_command(self):
        result, changed = self.apply(MODULE.NEEDLES[1] + "\n")
        self.assertTrue(changed)
        self.assertEqual(result.count(MODULE.REPLACEMENTS[1]), 1)
        self.assertNotIn(MODULE.NEEDLES[1], result)

    def test_already_patched_is_idempotent_for_both_commands(self):
        for replacement in MODULE.REPLACEMENTS:
            with self.subTest(replacement=replacement):
                result, changed = self.apply(replacement + "\n")
                self.assertFalse(changed)
                self.assertEqual(result, replacement + "\n")

    def test_fails_closed_if_upstream_command_drifts(self):
        with self.assertRaises(ValueError):
            self.apply('prospero-lld --unexpected-new-layout\n')

    def test_fails_closed_if_command_is_duplicated(self):
        with self.assertRaises(ValueError):
            self.apply(MODULE.NEEDLES[0] + "\n" + MODULE.NEEDLES[0] + "\n")

    def test_fails_closed_if_both_link_command_forms_exist(self):
        with self.assertRaises(ValueError):
            self.apply("\n".join(MODULE.NEEDLES))


if __name__ == "__main__":
    unittest.main()
