#!/usr/bin/env bash
# Prepare a disposable pinned Native Online checkout for a PS5/FreeBSD build.
# The game ISO and generated recompiler files must remain user-supplied/local.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="${1:-$ROOT/.work/reference-sources/tekken6-native-online-source}"
export T6_PS5_PORT_ROOT="$ROOT"
SDK="${T6_REXGLUE_SDK_ROOT:-$SOURCE/../rexglue-sdk}"
test -f "$SDK/include/rex/platform.h" || { echo "Missing pinned ReXGlue SDK at $SDK" >&2; exit 2; }
test -f "$SOURCE/CMakeLists.txt" || { echo "Missing Native Online source at $SOURCE" >&2; exit 2; }
bash "$ROOT/tools/apply_ggpo_posix_overlay.sh" "$SOURCE"
# Supply only the two header-only SDK submodules needed by the platform-boundary compile check.
for dep in fmt simde spdlog; do
    dep_source="$SOURCE/../$dep"
    test -d "$dep_source" || { echo "Missing pinned $dep dependency at $dep_source" >&2; exit 2; }
    mkdir -p "$SDK/thirdparty"
    rm -rf "$SDK/thirdparty/$dep"
    ln -s "$dep_source" "$SDK/thirdparty/$dep"
done
python3 - "$SOURCE" "$SDK" <<'PY'
from pathlib import Path
import sys
root = Path(sys.argv[1])
sdk = Path(sys.argv[2])

# The Native Online source targets ReXGlue 0.10; add the Prospero platform
# switch to that exact SDK instead of replacing it with the older 0.8 SDK in
# the separate PS5 example project.
platform = sdk / "include/rex/platform.h"
ptext = platform.read_text()
if "#if defined(__PROSPERO__)" not in ptext:
    marker = "#if defined(TARGET_OS_MAC) && TARGET_OS_MAC\n"
    if marker not in ptext:
        raise SystemExit("Could not locate ReXGlue platform selection")
    ptext = ptext.replace(marker, "#if defined(__PROSPERO__)\n#define REX_PLATFORM_PROSPERO 1\n#elif defined(TARGET_OS_MAC) && TARGET_OS_MAC\n", 1)
if "#ifndef REX_PLATFORM_PROSPERO" not in ptext:
    marker = "#ifndef REX_PLATFORM_MAC\n"
    if marker not in ptext:
        raise SystemExit("Could not locate ReXGlue platform macro defaults")
    ptext = ptext.replace(marker, "#ifndef REX_PLATFORM_PROSPERO\n#define REX_PLATFORM_PROSPERO 0\n#endif\n" + marker, 1)
platform.write_text(ptext)

# The PS5 SDK libc++ lacks floating-point std::from_chars. ReXGlue already
# has a C-locale fallback for AppleClang; enable the same fallback on Prospero.
numeric = sdk / "include/rex/string/numeric.h"
ntext = numeric.read_text()
ntext = ntext.replace("#if REX_PLATFORM_MAC\n#include <locale.h>", "#if REX_PLATFORM_MAC || REX_PLATFORM_PROSPERO\n#include <locale.h>", 1)
ntext = ntext.replace("#if REX_PLATFORM_MAC\ntemplate <typename T>\ninline std::from_chars_result portable_float_from_chars", "#if REX_PLATFORM_MAC || REX_PLATFORM_PROSPERO\ntemplate <typename T>\ninline std::from_chars_result portable_float_from_chars", 1)
ntext = ntext.replace("#if REX_PLATFORM_MAC\n    auto [p, error] = portable_float_from_chars", "#if REX_PLATFORM_MAC || REX_PLATFORM_PROSPERO\n    auto [p, error] = portable_float_from_chars", 1)
# The vector parser has a second floating-point from_chars call; route all Mac fallback
# branches through the same locale-stable parser on Prospero.
ntext = ntext.replace("#if REX_PLATFORM_MAC", "#if REX_PLATFORM_MAC || REX_PLATFORM_PROSPERO")
ntext = ntext.replace("#if REX_PLATFORM_MAC || REX_PLATFORM_PROSPERO || REX_PLATFORM_PROSPERO", "#if REX_PLATFORM_MAC || REX_PLATFORM_PROSPERO")
if ntext.count("#if REX_PLATFORM_MAC || REX_PLATFORM_PROSPERO") < 3:
    raise SystemExit("Could not enable all ReXGlue floating-point parser fallbacks")
numeric.write_text(ntext)

# PS5 libc++ lacks clock_time_conversion/clock_cast; use the SDK's existing
# Apple compatibility shim for this platform too.
chrono = sdk / "include/rex/chrono/chrono.h"
ctext = chrono.read_text()
ctext = ctext.replace("#ifdef __APPLE__\n// Apple libc++ does not expose clock_time_conversion or clock_cast.", "#if defined(__APPLE__) || defined(__PROSPERO__)\n// Apple and PS5 libc++ do not expose clock_time_conversion or clock_cast.", 1)
if "#if defined(__APPLE__) || defined(__PROSPERO__)" not in ctext:
    raise SystemExit("Could not enable ReXGlue chrono compatibility shim")
chrono.write_text(ctext)


# Replace Win32 VirtualQuery in the game's snapshot page walker with ReXGlue's
# native memory-protection query on PS5. This preserves the committed/readable
# page filter required by rollback snapshots rather than guessing from mincore.
netplay = root / "src/t6_netplay_internal.h"
ntext = netplay.read_text()
if "#include <rex/memory/utils.h>" not in ntext:
    marker = "#include <rex/ppc/func.h>\n"
    if marker not in ntext:
        raise SystemExit("Could not add ReXGlue memory-query header")
    ntext = ntext.replace(marker, marker + "#include <rex/memory/utils.h>\n", 1)
pattern = r"// Committed, readable host pages of guest range \[lo, hi\)\ntemplate <typename Fn>\nvoid ForEachCommitted\(uint32_t lo, uint32_t hi, const Fn& fn\) \{.*?\n\}"
import re
match = re.search(pattern, ntext, flags=re.S)
if not match:
    raise SystemExit("Could not locate snapshot committed-page walker")
original = match.group(0)
if "#if defined(__PROSPERO__)" not in original:
    brace = original.index("{")
    body = original[brace + 1:original.rfind("}")]
    replacement = original[:brace + 1] + r"""
#if defined(__PROSPERO__)
  const uint64_t page_size = rex::memory::page_size();
  uint64_t a = lo;
  while (a < hi) {
    const uint64_t page = a & ~(page_size - 1);
    size_t region_length = 0;
    rex::memory::PageAccess access = rex::memory::PageAccess::kNoAccess;
    if (!rex::memory::QueryProtect(g_t6_membase + page, region_length, access) || !region_length) {
      a = std::min<uint64_t>((page + page_size), hi);
      continue;
    }
    const uint64_t region_end = page + region_length;
    const uint64_t end = std::min<uint64_t>(region_end, hi);
    const bool readable = access == rex::memory::PageAccess::kReadOnly ||
                          access == rex::memory::PageAccess::kReadWrite ||
                          access == rex::memory::PageAccess::kExecuteReadOnly ||
                          access == rex::memory::PageAccess::kExecuteReadWrite;
    if (readable && end > a) fn(static_cast<uint32_t>(a), static_cast<uint32_t>(end - a));
    if (end <= a) {
      a = std::min<uint64_t>((page + page_size), hi);
    } else {
      a = end;
    }
  }
#else
""" + body + r"""
#endif
}"""
    ntext = ntext[:match.start()] + replacement + ntext[match.end():]
netplay.write_text(ntext)


# Windows vectored-exception handling is unavailable on PS5; install POSIX fatal
# signal handlers while keeping the detailed Win32 handler for the PC build.
crash = root / "src/t6_crash.cpp"
crash_text = crash.read_text()
if "#if defined(__PROSPERO__)" not in crash_text:
    marker = '#include "t6_netplay_internal.h"\n'
    if marker not in crash_text:
        raise SystemExit("Could not locate crash-handler include")
    ps5_handler = r'''
#if defined(__PROSPERO__)
#include <csignal>
#include <cstdlib>
namespace t6np {
static void T6CrashSignal(int signal_number) {
  REXLOG_ERROR("T6 crash: PS5 host signal {}", signal_number);
  if (auto fn = T6Rex().current_guest_context) {
    if (auto* c = static_cast<PPCContext*>(fn())) {
      REXLOG_ERROR("T6 crash: guest lr {:08X} r1 {:08X} r3 {:08X} r4 {:08X} r30 {:08X} r31 {:08X}",
                   static_cast<uint32_t>(c->lr), c->r1.u32, c->r3.u32, c->r4.u32, c->r30.u32, c->r31.u32);
    }
  }
  std::abort();
}
struct T6CrashInstall {
  T6CrashInstall() {
    std::signal(SIGSEGV, T6CrashSignal);
    std::signal(SIGBUS, T6CrashSignal);
    std::signal(SIGILL, T6CrashSignal);
    std::signal(SIGFPE, T6CrashSignal);
  }
} g_t6_crash_install;
}  // namespace t6np
#else
'''
    crash_text = crash_text.replace(marker, marker + ps5_handler, 1)
    crash_text += "\n#endif  // __PROSPERO__\n"
crash.write_text(crash_text)


# The optional customization research watch relies on Win32 vectored exceptions
# and the x86 trap flag. Keep it intact on PC, but compile an explicit disabled
# stub on PS5 instead of pretending POSIX signals are ABI-equivalent.
research = root / "src/t6_research.cpp"
rtext = research.read_text()
pattern = r"LONG WINAPI CwHandler\(EXCEPTION_POINTERS\* ep\) \{.*?\n\}\n\nvoid CwStart\(uint8_t\* base, uint32_t rec, uint32_t len\) \{.*?\n\}\n\nvoid CwStop\(\) \{.*?\n\}"
match = re.search(pattern, rtext, flags=re.S)
if not match:
    raise SystemExit("Could not locate Win32-only customization watch handler")
block = match.group(0)
if "#if !defined(__PROSPERO__)" not in block:
    replacement = "#if !defined(__PROSPERO__)\n" + block + r"""
#else
void CwStart(uint8_t*, uint32_t, uint32_t) {
  REXLOG_WARN("T6 custom watch requires Win32 vectored exceptions; disabled on PS5");
}
void CwStop() {}
#endif
"""
    rtext = rtext[:match.start()] + replacement + rtext[match.end():]
research.write_text(rtext)

# Port session-level Windows diagnostics/input probes without changing the
# deterministic rollback/session logic. Keep PC behavior unchanged.
session = root / "src/t6_session.cpp"
stext = session.read_text()

# Machine telemetry is a Windows-only diagnostic; PS5 logs a concise native line.
import re
log_pattern = r"void LogSystemOnce\(\) \{.*?\n\}"
log_match = re.search(log_pattern, stext, flags=re.S)
if not log_match:
    raise SystemExit("Could not locate LogSystemOnce")
if "#if defined(__PROSPERO__)" not in log_match.group(0):
    stext = stext[:log_match.start()] + r'''void LogSystemOnce() {
#if defined(__PROSPERO__)
  static bool done = false;
  if (done) return;
  done = true;
  REXLOG_INFO("T6 system: running on native Prospero; OS telemetry unavailable");
#else
''' + log_match.group(0)[len("void LogSystemOnce() {"):-1] + r'''
#endif
}''' + stext[log_match.end():]

# Windows thread priority tuning is optional and not equivalent to Prospero scheduling.
prio = '''  if (T6Env("T6_NET_PRIO")) {
    SetProcessPriorityBoost(GetCurrentProcess(), TRUE);
    SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_ABOVE_NORMAL);
    REXLOG_INFO("T6 net: priority boost off, main thread above normal");
  }'''
if prio in stext:
    stext = stext.replace(prio, '''#if !defined(__PROSPERO__)
''' + prio + '''
#else
  if (T6Env("T6_NET_PRIO"))
    REXLOG_WARN("T6_NET_PRIO is a Windows-only experiment and is ignored on PS5");
#endif''', 1)

# Address length is checked above; memcpy + terminator is portable and bounded.
stext = stext.replace("strcpy_s(pl.u.remote.ip_address, c.remote_ip.c_str());",
                      "std::memcpy(pl.u.remote.ip_address, c.remote_ip.c_str(), c.remote_ip.size() + 1);", 1)
# Compiler-independent bit counts for input diagnostics.
stext = stext.replace("__popcnt((local[0] & ~g_last_sent[0]) & 0xFF)",
                      "__builtin_popcount((local[0] & ~g_last_sent[0]) & 0xFF)", 1)
stext = stext.replace("__popcnt((local[1] & ~g_last_sent[1]) & 0x0F)",
                      "__builtin_popcount((local[1] & ~g_last_sent[1]) & 0x0F)", 1)

# WinMM joystick polling is not the PS5 controller API. Disable only the optional
# Windows diagnostic thread; actual controller integration remains a separate task.
input_pattern = r"void InputDiagThread\(\) \{.*?\n\}"
input_match = re.search(input_pattern, stext, flags=re.S)
if not input_match:
    raise SystemExit("Could not locate InputDiagThread")
if "#if !defined(__PROSPERO__)" not in input_match.group(0):
    original = input_match.group(0)
    replacement = "#if !defined(__PROSPERO__)\n" + original + r'''
#else
void InputDiagThread() {
  REXLOG_WARN("T6 input diagnostics: WinMM joystick polling is unavailable on PS5");
}
#endif
'''
    stext = stext[:input_match.start()] + replacement + stext[input_match.end():]
session.write_text(stext)

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
