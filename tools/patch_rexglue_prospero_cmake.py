#!/usr/bin/env python3
"""Patch the pinned ReXGlue SDK's CMake platform selection for an explicit Prospero target."""
from __future__ import annotations

import argparse
from pathlib import Path

PLATFORM_NEEDLE = '''if(WIN32)
    if(REX_TARGET_PROCESSOR MATCHES "AMD64|x86_64")
        set(REX_PLATFORM "win-amd64")
'''
PLATFORM_REPLACEMENT = '''option(REX_PLATFORM_PROSPERO "Build the ReXGlue SDK for PlayStation 5 Prospero" OFF)

if(REX_PLATFORM_PROSPERO)
    if(NOT REX_TARGET_PROCESSOR MATCHES "AMD64|x86_64")
        message(FATAL_ERROR "Prospero builds require the 64-bit x86 target")
    endif()
    set(REX_PLATFORM "prospero-amd64")
    add_compile_definitions(REX_PLATFORM_PROSPERO=1)
elseif(WIN32)
    if(REX_TARGET_PROCESSOR MATCHES "AMD64|x86_64")
        set(REX_PLATFORM "win-amd64")
'''
RPATH_NEEDLE = "if(UNIX AND NOT APPLE)\n    # Keep installed binaries self-contained by resolving shared libs relative"
RPATH_REPLACEMENT = "if(UNIX AND NOT APPLE AND NOT REX_PLATFORM_PROSPERO)\n    # Keep installed binaries self-contained by resolving shared libs relative"
OPTION_LINE = 'option(REX_PLATFORM_PROSPERO "Build the ReXGlue SDK for PlayStation 5 Prospero" OFF)'
UI_PLATFORM_NEEDLE = '''if(WIN32)
    set(REXUI_PLATFORM_SOURCES
        surface_win.cpp
    )
elseif(APPLE)
'''
UI_PLATFORM_REPLACEMENT = '''if(REX_PLATFORM_PROSPERO)
    # Prospero does not use the Linux X11/Wayland surface implementation.
    set(REXUI_PLATFORM_SOURCES)
elseif(WIN32)
    set(REXUI_PLATFORM_SOURCES
        surface_win.cpp
    )
elseif(APPLE)
'''
UI_DEPS_NEEDLE = "if(UNIX AND NOT APPLE)\n    find_package(PkgConfig REQUIRED)\n    pkg_check_modules(X11_XCB REQUIRED x11-xcb)"
UI_DEPS_REPLACEMENT = "if(UNIX AND NOT APPLE AND NOT REX_PLATFORM_PROSPERO)\n    find_package(PkgConfig REQUIRED)\n    pkg_check_modules(X11_XCB REQUIRED x11-xcb)"


def replace_once(source: str, old: str, new: str, label: str) -> tuple[str, bool]:
    if old in source:
        if source.count(old) != 1:
            raise ValueError(f"Expected exactly one {label} block")
        return source.replace(old, new, 1), True
    if new in source:
        return source, False
    raise ValueError(f"Could not locate the pinned {label} block")


def patch_cmake(path: Path) -> bool:
    source = path.read_text(encoding="utf-8")
    changed = False

    if OPTION_LINE not in source:
        if source.count(PLATFORM_NEEDLE) != 1:
            raise ValueError("Expected exactly one pinned ReXGlue platform-selection block")
        source = source.replace(PLATFORM_NEEDLE, PLATFORM_REPLACEMENT, 1)
        changed = True
    elif source.count('set(REX_PLATFORM "prospero-amd64")') != 1:
        raise ValueError("Prospero option exists but its platform-selection block is incomplete")

    source, did_change = replace_once(source, RPATH_NEEDLE, RPATH_REPLACEMENT, "ELF RPATH")
    changed |= did_change
    if changed:
        path.write_text(source, encoding="utf-8")

    ui_path = path.parent / "src" / "ui" / "CMakeLists.txt"
    if ui_path.exists():
        ui = ui_path.read_text(encoding="utf-8")
        ui, a = replace_once(ui, UI_PLATFORM_NEEDLE, UI_PLATFORM_REPLACEMENT, "ReXUI platform source")
        ui, b = replace_once(ui, UI_DEPS_NEEDLE, UI_DEPS_REPLACEMENT, "ReXUI Linux dependencies")
        if a or b:
            ui_path.write_text(ui, encoding="utf-8")
            changed = True
    return changed


FFMPEG_CONFIG_NEEDLE = '''#elif defined(__ANDROID__)
'''
FFMPEG_CONFIG_REPLACEMENT = '''#elif defined(__FreeBSD__) || defined(__PROSPERO__)
#include "config_linux_x86_64.h"
#elif defined(__ANDROID__)
'''


def patch_ffmpeg_config(sdk_root: Path) -> bool:
    """Use the pinned x86_64 POSIX capability profile for Prospero's libc.

    This prevents the vendored FFmpeg config dispatcher from stopping at
    '#error no config' on PS5. It is a bootstrap compatibility profile, not a
    claim that every Linux libc feature is identical on Prospero.
    """
    path = sdk_root / "thirdparty" / "FFmpeg" / "config.h"
    if not path.is_file():
        raise ValueError(f"Missing pinned FFmpeg config header: {path}")
    source = path.read_text(encoding="utf-8")
    if '#elif defined(__FreeBSD__) || defined(__PROSPERO__)' in source:
        return False
    if source.count(FFMPEG_CONFIG_NEEDLE) != 1:
        raise ValueError("Could not locate the pinned FFmpeg config dispatcher")
    if not (path.parent / "config_linux_x86_64.h").is_file():
        raise ValueError("Pinned FFmpeg Linux x86_64 config header is missing")
    path.write_text(source.replace(FFMPEG_CONFIG_NEEDLE, FFMPEG_CONFIG_REPLACEMENT, 1), encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sdk_root", type=Path, help="ReXGlue SDK checkout root")
    args = parser.parse_args()
    target = args.sdk_root / "CMakeLists.txt"
    try:
        changed = patch_cmake(target)
        ffmpeg_changed = patch_ffmpeg_config(args.sdk_root)
        changed = changed or ffmpeg_changed
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    print("Patched ReXGlue/FFmpeg platform selection for Prospero." if changed else "Prospero CMake and FFmpeg patches already present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
