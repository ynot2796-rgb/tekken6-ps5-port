#!/usr/bin/env bash
# Fetch pinned, already-existing source implementations used to guide the port.
# No proprietary game files are fetched or copied.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${T6_REFERENCE_ROOT:-$ROOT/.work/reference-sources}"
TEKKEN_REV=24db272e03ab0e6c35f22abea519e76b22ecf450
PROSPERO_BUILDER_REV=59e7086b8f920f70630d9461d357d0f6428fe4cc
REXGLUE_REV=f5337cdc947ff6d4c4196737e2c807a48f2a1fc2
FMT_REV=407c905e45ad75fc29bf0f9bb7c5c2fd3475976f
SIMDE_REV=71fd833d9666141edcd1d3c109a80e228303d8d7
SPDLOG_REV=79524ddd08a4ec981b7fea76afd08ee05f83755d

checkout_pin() {
    local name="$1" url="$2" revision="$3"
    local path="$DEST/$name"
    if [[ -d "$path/.git" ]]; then
        git -C "$path" fetch --depth=1 origin "$revision"
    else
        mkdir -p "$path"
        git -C "$path" init -q
        git -C "$path" remote add origin "$url"
        git -C "$path" fetch --depth=1 origin "$revision"
    fi
    git -C "$path" checkout -q --detach FETCH_HEAD
    local actual
    actual="$(git -C "$path" rev-parse HEAD)"
    [[ "$actual" == "$revision" ]] || {
        echo "Pin mismatch for $name: expected $revision, got $actual" >&2
        exit 2
    }
    printf '%s %s %s\n' "$name" "$revision" "$url"
}

mkdir -p "$DEST"
{
    echo "Tekken 6 PS5 port reference-source audit"
    echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    checkout_pin tekken6-native-online-source \
        https://github.com/Ekspym/tekken6-native-online-source.git "$TEKKEN_REV"
    checkout_pin prospero-recomp-reference \
        https://github.com/LoZazaMastro/TheSimpsonsGame-PS5-Builder.git "$PROSPERO_BUILDER_REV"
    checkout_pin rexglue-sdk \
        https://github.com/rexglue/rexglue-sdk.git "$REXGLUE_REV"
    checkout_pin fmt \
        https://github.com/fmtlib/fmt.git "$FMT_REV"
    checkout_pin simde \
        https://github.com/simd-everywhere/simde.git "$SIMDE_REV"
    checkout_pin spdlog \
        https://github.com/gabime/spdlog.git "$SPDLOG_REV"
} | tee "$DEST/PINNED_SOURCES.txt"

T="$DEST/tekken6-native-online-source"
P="$DEST/prospero-recomp-reference"
R="$DEST/rexglue-sdk"
F="$DEST/fmt"
S="$DEST/simde"
D="$DEST/spdlog"
test -f "$T/CMakeLists.txt"
test -f "$T/src/t6_netplay.cpp"
test -f "$T/third_party/ggpo/src/include/ggponet.h"
test -f "$P/prospero/ps5-toolchain.cmake"
test -f "$P/prospero/build.sh"
test -f "$P/tools/rexglue-sdk/CMakeLists.txt"
test -f "$R/include/rex/cvar.h"
test -f "$R/include/rex/system/xthread.h"
test -f "$F/include/fmt/format.h"
test -f "$S/simde/x86/sse.h"
test -f "$D/include/spdlog/spdlog.h"

{
    echo
    echo "## Verified source facts"
    echo "- Tekken source commit: $(git -C "$T" rev-parse HEAD)"
    echo "- PS5 ReXGlue reference commit: $(git -C "$P" rev-parse HEAD)"
    echo "- ReXGlue SDK revision: $(git -C "$R" rev-parse HEAD)"
    echo "- ReXGlue SDK version: $(grep -m1 'project(ReXGlue' "$R/CMakeLists.txt" || true)"
    echo "- fmt revision: $(git -C "$F" rev-parse HEAD)"
    echo "- simde revision: $(git -C "$S" rev-parse HEAD)"
    echo "- spdlog revision: $(git -C "$D" rev-parse HEAD)"
    echo "- PS5 toolchain: present"
    echo "- ReXGlue Prospero option: $(grep -q 'REXGLUE_PLATFORM_PROSPERO' "$P/tools/rexglue-sdk/CMakeLists.txt" && echo present || echo MISSING)"
    echo "- Tekken Windows socket link: $(grep -n 'ws2_32 winmm' "$T/CMakeLists.txt" | head -n 1 || true)"
    echo "- Tekken Xenos GPU target: $(grep -n 'GPU_PLUGINS xenos' "$T/CMakeLists.txt" | head -n 1 || true)"
    echo "- GGPO UNIX backend header: $([[ -f "$T/third_party/ggpo/src/lib/ggpo/platform_linux.h" ]] && echo present || echo MISSING in pinned source tree)"
    echo "- GGPO UNIX backend implementation: $([[ -f "$T/third_party/ggpo/src/lib/ggpo/platform_linux.cpp" ]] && echo present || echo MISSING in pinned source tree)"
    echo "- GGPO poll implementation Win32 dependencies: $(grep -o 'CreateEvent\|WaitForMultipleObjects\|HANDLE' "$T/third_party/ggpo/src/lib/ggpo/poll.cpp" "$T/third_party/ggpo/src/lib/ggpo/poll.h" | cut -d: -f2 | sort -u | paste -sd ',' -)"
    echo "- PS5 reference Vulkan/RADV path: $(grep -n 'RADV_ARCHIVE\|libvulkan_radeon.ps5.a' "$P/prospero/build.sh" | head -n 1 || true)"
    echo
    echo "## Porting consequence"
    echo "Reuse the PS5 toolchain and ReXGlue Prospero runtime as the first integration base."
    echo "The Tekken game target is not yet a PS5 target: its current CMake links WinSock/winmm and requests the Xenos plugin."
    echo "No official matchmaking endpoint or certificate is inferred by this audit."
} | tee "$DEST/REFERENCE_SOURCE_AUDIT.md"

echo "Reference sources and audit are ready at: $DEST"
