#!/usr/bin/env python3
"""Add a native ReXGlue runtime + statically linked Xenos Vulkan smoke target."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: patch_rexglue_probe_target.py REXGLUE_SOURCE_ROOT")

root = Path(sys.argv[1]).resolve()
cmake = root / "CMakeLists.txt"
source = cmake.read_text(encoding="utf-8")
marker = "add_subdirectory(src/rexglue)"
target = """# Local PS5 integration smoke target; contains no generated game code.
add_executable(t6_rexglue_probe
    ${T6_PORT_ROOT}/native/rexglue_probe/main.cpp)
# Link the Xenos plugin into the title. Its static target carries the runtime
# and Vulkan/SPIR-V dependencies; the PS5 loader calls its linked factory.
target_link_libraries(t6_rexglue_probe PRIVATE rexgpu-xenos)
set_target_properties(t6_rexglue_probe PROPERTIES SUFFIX ".elf")
"""
if "add_executable(t6_rexglue_probe" in source:
    if target in source:
        print("ReXGlue probe target already present.")
        raise SystemExit(0)
    raise SystemExit("Existing ReXGlue probe target differs; refusing to overwrite it")
if source.count(marker) != 1:
    raise SystemExit("expected exactly one ReXGlue CMake insertion point")
cmake.write_text(source.replace(marker, marker + "\n" + target, 1), encoding="utf-8")
print("Added ReXGlue runtime + Xenos Vulkan native link probe.")
