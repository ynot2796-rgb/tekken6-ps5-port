#!/usr/bin/env python3
"""Add a small native ReXGlue runtime/plugin smoke executable to pinned SDK CMake."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: patch_rexglue_probe_target.py REXGLUE_SOURCE_ROOT")
root = Path(sys.argv[1]).resolve()
cmake = root / "CMakeLists.txt"
text = cmake.read_text()
marker = "add_subdirectory(src/rexglue)"
block = """
# Local PS5 integration smoke target; does not contain generated game code.
add_executable(t6_rexglue_probe
    ${CMAKE_CURRENT_LIST_DIR}/../../../../native/rexglue_probe/main.cpp)
target_link_libraries(t6_rexglue_probe PRIVATE rexruntime)
"""
if "add_executable(t6_rexglue_probe" in text:
    raise SystemExit("probe target already present; refusing to patch twice")
if marker not in text:
    raise SystemExit("expected ReXGlue CMake insertion point not found")
# The SDK is checked out under .work/reference-sources/rexglue-sdk. Use the
# workspace path passed through T6_PORT_ROOT instead of a fragile relative path.
block = block.replace("${CMAKE_CURRENT_LIST_DIR}/../../../../native/rexglue_probe/main.cpp",
                      "${T6_PORT_ROOT}/native/rexglue_probe/main.cpp")
text = text.replace(marker, marker + "\n" + block, 1)
cmake.write_text(text)
