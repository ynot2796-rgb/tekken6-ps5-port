# SpeedBreaker PS5 reference audit and Tekken 6 integration decision

**Purpose:** Reuse proven PS5 homebrew platform work without replacing Tekken 6's own ReXGlue-generated game/runtime architecture with an unrelated emulator or game engine.

**Audited source:** [bystritskiy/speedbreaker-ps5](https://github.com/bystritskiy/speedbreaker-ps5), default branch `main`, README blob `63a6490ae031a57110edb5562eb70f61cdd11255`, inspected 30 October 2026. This is the PS5 fork, distinct from upstream [SpeedBreakerProject/speedbreaker](https://github.com/SpeedBreakerProject/speedbreaker).

## What SpeedBreaker proves (and what it does not)

The PS5 fork documents a native static-recompilation app for the Xbox 360 version of Need for Speed: Most Wanted (2005). Its README describes:
- XenonRecomp-generated C++ compiled for PS5 x86-64;
- a runtime implementing Xbox 360 kernel/system behavior, Xenos GPU command/shader translation, XMA audio and controller behavior;
- RADV linked into the app, with VideoOut display and AudioOut audio through SDL3;
- DualSense support, saves/settings, shader cache, bug-report capture and native title packaging/deployment;
- a user-supplied game image workflow, with generated code and game files excluded from Git.

This is strong evidence that a full Xbox 360 static recompilation can be packaged as a native PS5 homebrew app. It is **not** evidence that Tekken 6's ReXGlue runtime or renderer already builds on PS5. SpeedBreaker's own runtime and GPU implementation are separate projects.

## Reuse matrix

| Area | SpeedBreaker PS5 reference | Tekken 6 decision |
|---|---|---|
| PS5 title lifecycle / startup | Native PS5 app, deployment and packaging flow | Reuse build and lifecycle patterns after comparing SDK/toolchain versions; do not copy its game-specific entry point |
| RADV / Vulkan linkage | Static RADV runtime in the app | Reuse as a reference for exact linker inputs and pinned Mesa provenance; do not mix archives from different SDK/Mesa revisions |
| Display | VideoOut-backed display through SDL3 | Prefer the already-selected Tekken native display/presentation boundary; adapt VideoOut/WSI only where the interfaces match |
| Xenos GPU | SpeedBreaker runtime translates Xenos commands/shaders | Do not import its entire renderer as a drop-in. First build the pinned ReXGlue Xenos Vulkan plugin against the same PS5 Vulkan stack |
| CPU recompilation | XenonRecomp PowerPC-to-C++ pipeline | ReXGlue-generated Tekken code is a different pipeline/ABI. Keep its code generator and generated-code contract |
| Input | DualSense exposed through SDL3 virtual gamepad | Use the native `scePad` sampling pattern; map to Tekken input once per deterministic simulation frame |
| Audio | XMA decode and SDL3/AudioOut path | Reuse only the PS5 AudioOut sink pattern. Tekken's XMA/audio callback and buffering need an explicit adapter |
| Storage | Separate app and writable user-data locations | Define read-only game-data and writable saves/config/log paths for Tekken; never assume SpeedBreaker's directory layout |
| Diagnostics | On-console log, hang/crash report and screenshot bundle | Add equivalent diagnostics to the Tekken shell so black screen, import failure and renderer failure can be distinguished |
| Licensing | GPL-3.0-or-later project with separately licensed dependencies | Treat its implementation code as GPL-covered unless a file's license says otherwise. Prefer interface/behavior study; do not copy code into a differently licensed project without an explicit compatible licensing decision and required notices/source obligations |

## Architecture decision

**Primary game path remains:**

1. User-owned compatible Tekken 6 Xbox 360 image → the pinned ReXGlue/XEX code-generation tools on the host.
2. Generated Tekken code + Native Online game-side code → PS5 target compilation.
3. ReXGlue runtime and Xenos GPU plugin → Prospero platform adaptations and the pinned PS5 Vulkan/RADV stack.
4. Native PS5 title shell → DualSense, VideoOut presentation, AudioOut, storage, timing, logging and package/deploy.
5. GGPO rollback/session integration → deterministic game input/state callbacks; only after local deterministic tests pass.

SpeedBreaker is a reference for stages 3–4, not a replacement for stages 1–2. TTT2-Recomp-PS5 remains a useful fighting-game reference for the D3D11/DXVK-native-to-RADV approach, but its renderer path is not automatically the correct choice for Tekken 6: the current Tekken source explicitly requests ReXGlue's Xenos GPU plugin, and the pinned ReXGlue source already contains a Vulkan Xenos implementation behind its Vulkan build option.

## Implementation gates (ordered to avoid wasted work)

### Gate 1 — Freeze one compatible PS5 platform stack
- Record exact PayloadSDK/Prospero toolchain, clang/lld, Mesa/RADV archive, Vulkan headers, module stubs and linker-script revisions.
- Compare those revisions with the existing native probe and the pinned ReXGlue SDK patch set.
- Do not mix the SpeedBreaker, TTT2, Unleashed and PS5X360 toolchains by copying individual archives from each.

### Gate 2 — Make the existing ReXGlue Xenos/Vulkan target configure
- Keep ReXGlue code generation host-native; generated game code and runtime are target-compiled for PS5.
- Enable the existing Vulkan Xenos implementation and disable the D3D12 implementation for the PS5 target.
- Add the missing Prospero platform selection and isolate Windows-only UI/desktop dependencies from the game runtime.
- Produce a source-contract/configure report before attempting a full link.

### Gate 3 — Build a ReXGlue runtime harness
- Link the pinned ReXGlue runtime and Xenos Vulkan plugin into a minimal native title.
- Use the same RADV archive and linker provenance as the selected PS5 platform stack.
- Confirm imports, unresolved symbols, memory allocation/protection, thread startup, clock and filesystem behavior.
- Present a visible test frame and prove a DualSense input changes it. A black screen that stays alive is not a graphics pass.

### Gate 4 — Compile and link the generated Tekken target
- Generate code only from the user's own legally acquired compatible game image, locally.
- Keep generated code, extracted assets, XEX/ISO files and proprietary data out of public CI and commits.
- Resolve the actual generated-code ABI and unresolved symbols; do not substitute a fake game executable or call a scaffold a game build.

### Gate 5 — Gameplay, audio and rollback
- Prove scene rendering, menus, gameplay frame pacing, controller mapping and audio output on the console.
- Validate deterministic save/load/replay and rollback before enabling online matchmaking.
- Treat official lobby services, certificates, authentication, cross-play and newer Native Online release features as separate gates requiring legitimate compatible source/configuration and real tests.

## Immediate engineering tasks

1. Audit the PS5 fork's actual build/deploy scripts and the exact SDK/RADV pins; compare them to the Tekken repo's existing PS5 probe and linker recipe.
2. Add a small machine-checkable contract test for the ReXGlue Vulkan plugin's required source files, target options and forbidden Windows/D3D12 dependencies.
3. Fix the existing RADV public-stub/import gap identified in `docs/PS5X360_COMPONENT_COMPATIBILITY_MATRIX.md` before expanding the generic Vulkan probe.
4. Build the pinned ReXGlue Xenos Vulkan plugin as a standalone PS5 target; record compiler/linker output and every remaining unresolved symbol.
5. Only after that succeeds, attach the runtime harness and generated Tekken target.

## Explicit non-goals

- Do not link the Xenia guest CPU/kernel/runtime into the native Tekken executable merely because PS5X360 runs on the same console.
- Do not replace ReXGlue's generated game ABI with XenonRecomp output from another title.
- Do not import SpeedBreaker's full Xenos renderer or SDL3 stack without a file-by-file dependency, license and ABI review.
- Do not upload game images, XEX files, generated proprietary game code/assets, private certificates, Sony-owned runtime modules or secrets.
- Do not describe a compile, package, ELF link or process-liveness test as playable Tekken 6.

## References

- SpeedBreaker PS5 fork: https://github.com/bystritskiy/speedbreaker-ps5
- SpeedBreaker upstream: https://github.com/SpeedBreakerProject/speedbreaker
- Tekken's ReXGlue source and Vulkan renderer audit: `docs/PS5X360_REUSE_AND_RECOMP_INTEGRATION.md`
- Tekken's component compatibility matrix: `docs/PS5X360_COMPONENT_COMPATIBILITY_MATRIX.md`
- TTT2 PS5 reference: https://github.com/CrownWiZ/TTT2-Recomp-PS5
- Unleashed Prospero reference: https://github.com/Nazky/UnleashedRecomp-Prospero
