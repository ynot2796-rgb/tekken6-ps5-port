#!/usr/bin/env python3
"""Regression tests for the temporary native ReXGlue link-probe target patch."""
from pathlib import Path
import subprocess
import tempfile

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "patch_rexglue_probe_target.py"
MARKER = "add_subdirectory(src/rexglue)"

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    cmake = root / "CMakeLists.txt"
    cmake.write_text("cmake_minimum_required(VERSION 3.25)\n" + MARKER + "\n")
    first = subprocess.run(["python3", str(SCRIPT), str(root)], text=True, capture_output=True)
    assert first.returncode == 0, first.stderr
    patched = cmake.read_text()
    assert "add_executable(t6_rexglue_probe" in patched
    assert "${T6_PORT_ROOT}/native/rexglue_probe/main.cpp" in patched
    assert "target_link_libraries(t6_rexglue_probe PRIVATE rexgpu-xenos)" in patched
    assert 'set_target_properties(t6_rexglue_probe PROPERTIES SUFFIX ".elf")' in patched
    second = subprocess.run(["python3", str(SCRIPT), str(root)], text=True, capture_output=True)
    assert second.returncode == 0, second.stderr
    assert cmake.read_text() == patched

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "CMakeLists.txt").write_text("project(no_insertion_point)\n")
    result = subprocess.run(["python3", str(SCRIPT), str(root)], text=True, capture_output=True)
    assert result.returncode != 0
    assert "insertion point" in result.stderr

print("ReXGlue native probe target patch tests passed.")
