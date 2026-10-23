#!/usr/bin/env bash
# Prepare a disposable pinned Native Online checkout for a PS5/FreeBSD build.
# The game ISO and generated recompiler files must remain user-supplied/local.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "\${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="\${1:-$ROOT/.work/reference-sources/tekken6-native-online-source}"
export T6_PS5_PORT_ROOT="$ROOT"
test -f "$SOURCE/CMakeLists.txt" || { echo "Missing Native Online source at $SOURCE" >&2; exit 2; }
bash "$ROOT/tools/apply_ggpo_posix_overlay.sh" "$SOURCE"
python3 - "$SOURCE" <<'PY'
from pathlib import Path
import sys
root = Path(sys.argv[1])
cmake = root / "CMakeLists.txt"
text = cmake.read_text()

old = '''# Small ISO inspection/extraction utility; game data remains local to the user.
add_subdirectory(tools/xdvdfs)
'''
new = '''# The ISO inspection utility is a host tool; do not cross-compile it into the PS5 title.
if(NOT CMAKE_CROSSCOMPILING)
    add_subdirectory(tools/xdvdfs)
endif()
'''
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit("Could not patch host-only xdvdfs utility target")

old = '''target_compile_definitions(ggpo PRIVATE _WINDOWS _WINSOCK_DEPRECATED_NO_WARNINGS _CRT_SECURE_NO_WARNINGS NOMINMAX)
target_compile_options(ggpo PRIVATE -w)
target_link_libraries(ggpo PUBLIC ws2_32 winmm)
'''
new = '''target_compile_options(ggpo PRIVATE -w)
if(WIN32)
    target_compile_definitions(ggpo PRIVATE _WINDOWS _WINSOCK_DEPRECATED_NO_WARNINGS _CRT_SECURE_NO_WARNINGS NOMINMAX)
    target_link_libraries(ggpo PUBLIC ws2_32 winmm)
else()
    # The POSIX overlay provides platform_linux.h/.cpp and the socket shim.
    target_include_directories(ggpo PRIVATE "$ENV{T6_PS5_PORT_ROOT}/include/ps5_compat" "$ENV{T6_PS5_PORT_ROOT}/include")
endif()
'''
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit("Could not patch Windows-only GGPO compile/link settings")

old = 'target_link_libraries(tekken6 PRIVATE ggpo)\n'
new = '''target_link_libraries(tekken6 PRIVATE ggpo)
if(NOT WIN32)
    target_include_directories(tekken6 PRIVATE "$ENV{T6_PS5_PORT_ROOT}/include/ps5_compat" "$ENV{T6_PS5_PORT_ROOT}/include")
endif()
'''
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit("Could not add PS5 compatibility include paths to the game target")

cmake.write_text(text)
print("Prepared POSIX GGPO, host-tool exclusion, and PS5 host-API include paths.")
print("Generated ReXGlue files and a compatible user-owned Tekken 6 ISO are still required to build the game.")
PY
