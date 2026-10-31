#!/usr/bin/env bash
# Run the upstream ReXGlue code generator against the user's own Tekken 6 XEX.
# Generated game code and the XEX stay in the ignored .work directory.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
XEX="${1:-}"
if [[ -z "$XEX" || ! -f "$XEX" ]]; then
  echo "Usage: bash tools/run_local_tekken6_codegen.sh /absolute/path/to/Default.xex" >&2
  exit 2
fi
XEX="$(realpath "$XEX")"
EXPECTED="ee138a4fe8d32a0edc131451377f4377041a49626153fa992db24f5420a7f15c"
ACTUAL="$(sha256sum "$XEX" | awk '{print $1}')"
if [[ "$ACTUAL" != "$EXPECTED" ]]; then
  echo "Unsupported Default.xex SHA-256: $ACTUAL" >&2
  echo "Expected Tekken 6 USA/Europe Rev 1: $EXPECTED" >&2
  exit 3
fi

bash "$ROOT/tools/prepare_reference_sources.sh"
SRC="$ROOT/.work/reference-sources/tekken6-native-online-source"
SDK="$ROOT/.work/reference-sources/rexglue-sdk"
WORK="$ROOT/.work/tekken6-codegen-host"
mkdir -p "$SRC/game" "$WORK"
install -m 0644 "$XEX" "$SRC/game/Default.xex"
# The manifest expects this config beside the manifest, while upstream keeps
# the editable project config in builder/project.
install -m 0644 "$SRC/builder/project/tekken6_config.toml" "$SRC/tekken6_config.toml"

git -C "$SDK" submodule sync --recursive
git -C "$SDK" submodule update --init --recursive --depth 1
cmake -S "$SRC" -B "$WORK" -G Ninja \
  -DREXSDK_DIR="$SDK" \
  -DCMAKE_BUILD_TYPE=Release
# The retail image has one 1.36 MB function. ReXGlue defaults to a 1 MiB
# output budget, so raise its init-only CVar to 2 MiB before launching codegen.
# This keeps that function in one generated TU instead of warning and forcing
# an oversized bucket. Override only when deliberately testing another budget.
REX_MAX_FILE_SIZE_BYTES="${T6_REX_MAX_FILE_SIZE_BYTES:-2097152}" \
  cmake --build "$WORK" --target tekken6_codegen --parallel 2

STAMP="$SRC/generated/default/codegen.build.stamp"
SOURCES="$SRC/generated/default/sources.cmake"
test -f "$STAMP"
test -s "$SOURCES"
COUNT="$(find "$SRC/generated/default" -type f \\( -name '*.cpp' -o -name '*.cc' -o -name '*.cxx' \\) | wc -l | tr -d ' ')"
BYTES="$(du -sb "$SRC/generated/default" | awk '{print $1}')"
{
  echo "status=generated"
  echo "xex_sha256=$ACTUAL"
  echo "generated_cpp_files=$COUNT"
  echo "generated_tree_bytes=$BYTES"
  echo "generated_tree=$SRC/generated/default"
  echo "source_list=$SOURCES"
} | tee "$ROOT/.work/TEKKEN6_CODEGEN_RESULT.txt"
echo "Code generation succeeded. Keep .work local; do not commit or upload generated game code."
