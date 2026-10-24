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

    def test_skips_linux_ui_surface_and_x11_wayland_dependencies_for_prospero(self):
        ui = """if(WIN32)
    set(REXUI_PLATFORM_SOURCES
        surface_win.cpp
    )
elseif(APPLE)
    set(REXUI_PLATFORM_SOURCES
        surface_mac.cpp
    )
else()
    set(REXUI_PLATFORM_SOURCES
        surface_gnulinux.cpp
    )
endif()

if(UNIX AND NOT APPLE)
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(X11_XCB REQUIRED x11-xcb)
    pkg_check_modules(WAYLAND REQUIRED wayland-client)
endif()
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "CMakeLists.txt"
            target.write_text(BASE, encoding="utf-8")
            ui_path = root / "src" / "ui" / "CMakeLists.txt"
            ui_path.parent.mkdir(parents=True)
            ui_path.write_text(ui, encoding="utf-8")
            MODULE.patch_cmake(target)
            patched = ui_path.read_text(encoding="utf-8")
            self.assertIn("if(REX_PLATFORM_PROSPERO)", patched)
            self.assertIn("set(REXUI_PLATFORM_SOURCES)", patched)
            self.assertIn("if(UNIX AND NOT APPLE AND NOT REX_PLATFORM_PROSPERO)", patched)
            self.assertNotIn("pkg_check_modules(X11_XCB REQUIRED x11-xcb)", patched)

    def test_patch_is_idempotent(self):
        first, changed = self.apply(BASE)
        self.assertTrue(changed)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "CMakeLists.txt"
            path.write_text(first, encoding="utf-8")
            self.assertFalse(MODULE.patch_cmake(path))
            self.assertEqual(path.read_text(encoding="utf-8"), first)

    def test_adds_posix_config_fallback_for_prospero_ffmpeg(self):
        with tempfile.TemporaryDirectory() as directory:
            sdk = Path(directory)
            ffmpeg = sdk / "thirdparty" / "FFmpeg"
            ffmpeg.mkdir(parents=True)
            config = ffmpeg / "config.h"
            config.write_text("#if defined(__gnu_linux__)\n#include \"config_linux_x86_64.h\"\n#elif defined(__ANDROID__)\n#error \"no config\"\n#endif\n", encoding="utf-8")
            (ffmpeg / "config_linux_x86_64.h").write_text("#define HAVE_ROUND 1\n", encoding="utf-8")
            self.assertTrue(MODULE.patch_ffmpeg_config(sdk))
            patched = config.read_text(encoding="utf-8")
            self.assertIn("#elif defined(__FreeBSD__) || defined(__PROSPERO__)", patched)
            self.assertIn('#include "config_linux_x86_64.h"', patched)
            self.assertFalse(MODULE.patch_ffmpeg_config(sdk))

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
