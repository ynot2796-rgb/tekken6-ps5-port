# External PS5 recompilation resources

Research snapshot: 2026-10-31. These are implementation references, not dependencies automatically safe to copy. Verify each repository's current revision and licence before adopting code.

## Highest-value references

### 1. R-comp — closest architectural match

Repository: https://github.com/Phi1ow/360-rcomp

R-comp builds Xbox 360 static recompilations as native PS5 applications and uses the same broad stack as this project: ReXGlue Xenos, Vulkan, PS5 RADV, a PS5 platform layer, and an application shell.

Useful source paths:
- `platform/ps5/title/crt/rcomp_title_crt.cpp` — title entry/CRT, BSS, libc environment setup and init/fini arrays.
- `platform/ps5/tools/build_title.sh` — compile, PIE link, PS5 ELF conversion, signing and package sequence.
- `gpu/xenos/rexglue/patches/0010-linked-vulkan-loader.patch` — linked Vulkan loader integration.
- `gpu/vulkan/ps5/radv_title_main.c` and `gpu/vulkan/LINK_CONTRACT.md` — RADV title-side integration contract.
- `platform/ps5/input_ps5.cpp`, `platform/ps5/audio_output_ps5.cpp`, `platform/ps5/os_vm_ps5.cpp` — native input, audio and memory examples.

Important caution: its top-level README reports GTA IV/EFLC PS5 progress, but the platform README and comments in the CRT retain older or explicitly untested status statements. Treat the CRT as a source-level reference; independently verify every startup assumption on firmware 13.60.

R-comp is GPL-3.0-or-later. Do not copy its implementation into this repository without checking the licensing consequences and project licence compatibility. Its architecture, public interfaces and documented build stages can still guide an independent implementation.

### 2. TTT2-Recomp-PS5 — closest console and game-domain match

Repository: https://github.com/CrownWiZ/TTT2-Recomp-PS5

This is a native PS5 port of the Xbox 360 Tekken Tag Tournament 2 recompilation and explicitly targets firmware 13.60 / Relapse. Its October 28, 2026 progress report documents:
- A real PS5 payload smoke cycle through the Relapse ELF loader on TCP 9021.
- A PS5 title ELF link with `_start`, zero undefined symbols and a constrained system-module import list.
- DXVK-native linked statically with a custom `VK_KHR_display` WSI over `sceVideoOut`.
- A RADV-on-Prospero build and an M4 first-frame milestone still awaiting console validation.

Useful paths:
- `docs/superpowers/plans/2026-10-27-m3-prospero-console-boot.md`
- `docs/superpowers/plans/2026-10-27-m4-radv-first-frame.md`
- `tools/ps5/smoke/main.c`
- `tools/ps5/probe_sce_link.sh`
- `port/src/runtime/main.cpp`

The low-level PS5 startup, import resolution, memory, input, audio and display work is relevant. Its D3D11/DXVK graphics route is not a drop-in replacement for Tekken 6's ReXGlue Xenos renderer. The repo's current README describes M4 linking as complete but first-frame console validation as pending.

### 3. ps5link SDK — alternative native-title linker

Repository: https://github.com/Rufidj/ps5link-sdk

Contains a C linker and startup object for turning Prospero object files into a real PS5 title, with NID imports, PLT/GOT, SCE dynamic tables and examples for pad input and GPU drawing.

Useful paths:
- `linker/crt1.S`
- `linker/link_real.c`
- `examples/pad_input/main.c`
- `examples/gpu_cube/main.c`

This is a useful independent reference for title startup and packaging, but its README says it was tested on firmware 9.00 and does not establish 13.60 compatibility. It is GPL-3.0 and should not be transplanted without a licensing review.

### 4. PS5_Vulkan / RADV

Repository: https://github.com/mihawk-99/PS5_Vulkan

Relevant for the PS5 Vulkan driver, PS5 display/presentation path, validation and performance diagnostics. Use its pinned revisions and the compatible SDK/driver pairing from the PS5 recomp projects rather than mixing arbitrary Mesa and SDK revisions.

### 5. ReXGlue SDK and Xbox 360 recompilation references

- ReXGlue SDK: https://github.com/rexglue/rexglue-sdk
- ReXGlue wiki: https://github.com/rexglue/rexglue-sdk/wiki
- XenonRecomp: https://github.com/hedge-dev/XenonRecomp
- Xenia: https://github.com/xenia-project/xenia
- Awesome Xbox 360 recompilations: https://github.com/abduznik/awesome-x360-recomps

ReXGlue is experimental and not a turnkey Xbox 360 runtime. Xenia remains a major behavioural reference for guest CPU, memory, kernel, XAM, Xenos, audio and filesystem semantics. XenonRecomp and other static recompilers provide alternative analysis/codegen references; do not switch codegen frameworks without a measured reason.

## Recommended acceleration plan for Tekken 6

1. **Use R-comp as the primary ReXGlue/PS5 implementation reference.** Compare its linked Vulkan factory patch, PS5 RADV link contract, CRT and title-link stages against our pinned ReXGlue patch and Prospero builder.
2. **Use TTT2-Recomp-PS5 as the firmware-13.60 validation reference.** Reuse the test strategy and inspect its import/link failures, but keep our ReXGlue/Xenos backend.
3. **Get a tiny native PS5 title link working before attempting the full Tekken image.** First link a controlled entry point against ReXGlue runtime + Xenos static factory + RADV and verify symbols/imports. Then add PS5 input/audio/presentation and finally generated Tekken code.
4. **Do not mix unpinned dependency revisions.** Record the exact PS5 SDK, RADV/Mesa, LLVM, ReXGlue and linker commits for every build.
5. **Keep game data private.** Never put the user's XEX, ISO, generated recompilation files, title updates or proprietary assets into public GitHub or public CI artifacts.

## Current project status at time of research

The project has a successful ReXGlue/Xenos static archive build and archive inventory on commit `2f87f214`. The PS5 static GPU factory-loader patch then had a malformed unified-diff hunk; hunk counts were corrected in commit `89298830`. A fresh full build and renderer-only build are running against that corrected patch; the adapter contract job passed. This is not yet a linked or booted Tekken 6 title.
