# PS5X360 → native Tekken 6 compatibility matrix

**Audited source baseline:** PS5X360 v1.0.2, commit `0a178708ea2138413eea60eb7625496457455137`.
**Target:** a native PS5 title containing ReXGlue-generated Tekken 6 code and Native Online's rollback/session layer.
**Status rule:** source inspection is not a successful link or console test.

## Findings from exact source files

| Component | Evidence | Classification | Porting decision |
|---|---|---|---|
| PS5 title entry and process lifecycle | `src/native_game_main.cpp` calls PS5 user service, pad, splash-screen and title-exec APIs; owns the UI loop and emulator lifetime | **Adapter required** | Use the lifecycle pattern, not this file as a drop-in entry point. Replace `xe::Emulator`, Xenia window/presenter and Xenia logging dependencies with the native game/runtime equivalents. |
| PS5 title link and packaging | `tools/build-native-game.sh` compiles `app_crt.cpp`, calls the pinned `radv-link.sh` recipe, links the native target with Prospero LLD, creates SELF and packages the title | **Reuse as build reference** | Pin the same SDK/Mesa/toolchain provenance and adapt a separate Tekken target. Do not copy object paths or linker flags without resolving each referenced target and symbol. |
| Memory mapping | `platform/ps5/native_memory_calls.cpp` wraps `mmap/mprotect/munmap` using `sceKernelMmap/Mprotect/Munmap` and translates kernel error codes to `errno` | **Reusable candidate; validate ABI** | Reuse only if ReXGlue/runtime uses POSIX VM calls with matching page/alignment/protection assumptions. Do not import unrelated privileged helpers. |
| Timing | `patches/canary/xbox360ps5.patch` adapts `CLOCK_MONOTONIC_RAW` and host tick frequency for Prospero | **Adapt** | Use monotonic host time for service/timer needs; game simulation must be deterministic and frame/rollback coordinated. Never use wall-clock drift as the rollback simulation clock. |
| Filesystem and writable storage | Patch maps executable to `/app0/eboot.bin`, user data to `/download0` | **Adapt** | Define explicit read-only game-data and writable save/config/log roots. ReXGlue paths must not assume Windows drive letters or PC install paths. |
| Vulkan/RADV graphics | Native link script combines a pinned RADV archive, Agc stubs, SDK shared libraries and Mesa weak-symbol resolution; entry point uses Xenia Vulkan graphics and KHR_display | **Runtime-specific / high risk** | The link recipe is a strong reference, but Xenia's Vulkan graphics system and guest Xenos command translation are not a renderer for ReXGlue. A native renderer/backend boundary is still required. |
| DualSense input | Entry point polls `scePadReadState`, maps button/axis samples to Xenia's input driver | **Adapter required** | Reuse the low-level pad sampling pattern only after verifying the state layout; map to Tekken's native input abstraction and deterministic per-frame input capture. |
| Audio | Entry point constructs `xbox360ps5::NativeAudioSystem` through Xenia's APU interface | **Interface incompatible until adapted** | Implement or adapt a native audio sink for the generated game's audio callback/format. Do not link Xenia APU merely to obtain output. |
| Logging/crash reporting | Xenia logger mirror, PS5 kernel debug output and TCP diagnostic stream | **Reusable pattern** | Keep a low-overhead log/crash path independent of the game runtime. Treat TCP log transport as optional diagnostics, not a game network endpoint. |
| Xenia guest CPU/kernel/GPU and title loader | Entry point constructs `xe::Emulator`, calls `Setup` and `LaunchPath`; patch alters Xenia internals and platform source selection | **Do not reuse as native game runtime** | This is the emulator boundary. Native recompiled game code must not require the Xenia guest CPU, Xbox kernel emulation, or Xenos command processor unless a specific dependency is proven necessary. |
| GGPO rollback/session | Not part of the native Xenia title-entry recipe; Tekken Native Online source has its own GGPO/game-side integration | **Separate subsystem; preserve and adapt** | Keep GGPO rollback/session logic, port socket/time/thread abstractions and connect it to the generated game's frame/input/state APIs. A successful GGPO library build alone does not prove gameplay rollback. |
| Title updates / DLC | PS5X360 has a content installer and version-matched per-game patches for emulated Xbox 360 content | **Reference only** | Its Xbox 360 content install path is not a native Tekken title-update installer. Identify exact game revision and define a native port build/version manifest; do not claim Xbox title updates are usable by the native executable. |
| Online services | PS5X360's v1.0.2 notes report selected Halo 3 checks and MW2 matchmaking searches, not a confirmed complete joined match | **Not evidence of Tekken compatibility** | Native Online endpoint, certificate, authentication and protocol compatibility remain separate. Do not invent endpoints or bypass certificate checks. |

## Concrete integration contract

Before linking game code, define the following stable interfaces in the Tekken port:

1. **Platform lifecycle:** initialize/shutdown, PS5 title exit/restart, crash/log path.
2. **Memory:** allocate/free/protect/map with documented alignment, page size and executable-memory rules.
3. **Frame clock:** monotonic host clock for deadlines plus a deterministic simulation frame counter controlled by the game/rollback layer.
4. **Input:** sample DualSense once per frame, normalize buttons/axes, then provide the same captured input to simulation and rollback.
5. **Graphics:** generated game/render backend must expose a documented PS5 presentation path. RADV linkage alone does not implement the Xenos renderer.
6. **Audio:** generated game audio callback → PS5 output queue, with explicit sample format, channel count and buffering.
7. **Netplay:** GGPO callbacks bind to game save/load state, advance-frame and input functions; validate deterministic replay before live matchmaking.
8. **Build provenance:** pin SDK, clang/lld, RADV/Mesa source/archive, stubs and linker scripts to one known-compatible set. Keep proprietary game-generated sources/assets out of public CI.

## Build gates

- **Gate A — native shell:** link/package a PS5 title using the release-matched toolchain and show a visible frame/input response.
- **Gate B — generated-code ABI:** compile a tiny generated-code or runtime harness and link it to the shell; record unresolved symbols and ABI mismatches.
- **Gate C — game renderer:** prove a Tekken scene can be presented; the emulator's working Xenos renderer does not satisfy this gate.
- **Gate D — simulation/input:** boot into gameplay and validate frame pacing, controls and audio.
- **Gate E — rollback:** deterministic state save/load and replay tests pass locally before any online claim.
- **Gate F — service compatibility:** legitimate endpoint/configuration and a completed online match are tested on-console; cross-play is a separate test.

## Immediate next change

Do not continue expanding the unrelated Vulkan-template probe until its missing `radv_EnumeratePhysicalDevices` public-stub export is resolved. First add a reproducible source-contract audit around the PS5X360 release and use its native title link recipe as the basis for the shell. This matrix deliberately does **not** claim that a native Tekken executable has been linked or booted.
