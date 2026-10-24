import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "patch_rexglue_prospero_cmake.py"
SPEC = importlib.util.spec_from_file_location("patch_rexglue_prospero_cmake", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

BASE = """if(UNIX AND NOT APPLE)
    # Keep installed binaries self-contained by resolving shared libs relative
endif()

set(REX_TARGET_PROCESSOR "${CMAKE_SYSTEM_PROCESSOR}")
if(WIN32)
    if(REX_TARGET_PROCESSOR MATCHES "AMD64|x86_64")
        set(REX_PLATFORM "win-amd64")
    elseif(REX_TARGET_PROCESSOR MATCHES "aarch64|ARM64|arm64")
        set(REX_PLATFORM "win-arm64")
    else()
        message(FATAL_ERROR "Unsupported Windows architecture")
    endif()
elseif(UNIX AND NOT APPLE)
    set(REX_PLATFORM "linux-amd64")
endif()
"""


class ReXGlueProsperoCMakePatchTests(unittest.TestCase):
    def apply(self, source):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "CMakeLists.txt"
            path.write_text(source, encoding="utf-8")
            changed = MODULE.patch_cmake(path)
            return path.read_text(encoding="utf-8"), changed

    def test_adds_explicit_prospero_branch_and_skips_elf_rpath(self):
        result, changed = self.apply(BASE)
        self.assertTrue(changed)
        self.assertIn('option(REX_PLATFORM_PROSPERO "Build the ReXGlue SDK for PlayStation 5 Prospero" OFF)', result)
        self.assertIn('set(REX_PLATFORM "prospero-amd64")', result)
        self.assertIn("elseif(WIN32)", result)
        self.assertIn("if(UNIX AND NOT APPLE AND NOT REX_PLATFORM_PROSPERO)", result)
        self.assertNotIn("if(UNIX AND NOT APPLE)\n    # Keep installed binaries", result)

    def test_patch_is_idempotent(self):
        first, changed = self.apply(BASE)
        self.assertTrue(changed)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "CMakeLists.txt"
            path.write_text(first, encoding="utf-8")
            self.assertFalse(MODULE.patch_cmake(path))
            self.assertEqual(path.read_text(encoding="utf-8"), first)

    def test_fails_closed_if_platform_block_drifts(self):
        with self.assertRaises(ValueError):
            self.apply(BASE.replace('set(REX_PLATFORM "win-amd64")', 'set(REX_PLATFORM "windows-x64")'))

    def test_fails_closed_if_rpath_block_is_missing(self):
        with self.assertRaises(ValueError):
            self.apply(BASE.replace("if(UNIX AND NOT APPLE)\n    # Keep installed binaries self-contained by resolving shared libs relative", "if(FALSE)"))

    def test_fails_closed_if_prospero_option_is_partial(self):
        partial = BASE.replace('if(WIN32)', 'option(REX_PLATFORM_PROSPERO "Build the ReXGlue SDK for PlayStation 5 Prospero" OFF)\nif(WIN32)', 1)
        with self.assertRaises(ValueError):
            self.apply(partial)


if __name__ == "__main__":
    unittest.main()
