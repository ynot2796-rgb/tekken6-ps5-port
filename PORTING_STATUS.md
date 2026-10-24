# Porting status

## Confirmed from upstream source

- Native Online is a native Windows PC project, not an emulator package.
- It recompiles Xbox 360 game code through ReXGlue.
- It includes rollback networking based on a GGPO fork and game-side netplay/session/input integration.
- The public source does not include game code/data.
- The public source README says the official server address, release API, pinned server certificate, and launcher artwork are not published.
- The upstream CMake configuration links GGPO with Windows-specific libraries (`ws2_32`, `winmm`), uses a Xenos GPU plugin, applies x86-specific compiler flags, and configures Windows GUI entry points. This is not currently a PS5 build configuration.
- The public source repository is pinned at commit `24db272e03ab0e6c35f22abea519e76b22ecf450` (source release 2.3.5, dated 21 October 2026). The separate Native Online release repository has since published v2.4.0, v2.4.1 and v2.4.2 on 22–23 October 2026. Their release notes describe group lobbies/live spectating, rollback-related crash fixes, and a performance fix, but those later patch implementations are not present in the public source commit. Do not claim the native port includes the 2.4.x patches until matching source or a legitimate, testable implementation is available. References: https://github.com/Ekspym/tekken6-native-online-source/commit/24db272e03ab0e6c35f22abea519e76b22ecf450 and https://github.com/Ekspym/Tekken6-native-online/releases/latest.

## Updated strategy — reuse PS5X360's native Xenia platform work

The project direction remains a native PS5 Tekken 6 port with the updated/recompiled game and online features. Reuse PS5X360/Xenia code wherever it reduces duplicated platform work; do not mistake a working emulator for an already-working native recompile.

Source checked on 23 October 2026:
- Repository: https://github.com/BrinooTk/PS5X360 (MIT project license; bundled dependencies keep their own licenses).
- Latest release source observed: v1.0.2, release commit `0a178708ea2138413eea60eb7625496457455137`.
- Release assets include `PS5X360-source-1.0.2-changes.zip`; use that matching source snapshot and its license notices when reviewing the shipped build, rather than assuming the current default-branch files alone exactly match the binary.
- PS5X360's Xenia patch includes Prospero platform selection, POSIX source selection, PS5 clock/filesystem/logging adjustments, PS5-native memory/fault handling, a native game target and an explicit native title link/package recipe. Its build recipe links Xenia core libraries and RADV/Mesa platform libraries into a PS5 title.
- v1.0.2 release notes say online requests no longer hang; Halo 3 sessions/connection checks/leaderboards and Modern Warfare 2 matchmaking searches were checked on a PS5, but a complete joined multiplayer match was not yet confirmed. This does not prove Tekken 6 online works.

Priority change:
1. Audit the exact v1.0.2 source snapshot and build recipes for reusable PS5 title lifecycle, RADV/Vulkan linkage, memory mappings, clocks, filesystem, logging, input/audio platform services, and Xenia's native-game target.
2. Compare those platform adapters against our current ReXGlue-generated-game and GGPO integration. Port/adapt compatible pieces into our native port; do not copy the whole emulator wholesale or link incompatible SDK/Mesa versions.
3. Keep the existing graphics/input probe as a fallback validation tool, but do not spend effort recreating PS5 graphics/runtime infrastructure before the PS5X360 reuse audit is complete.
4. Separately generate the Tekken 6 game code from the compatible user-owned game image, then integrate it with the reused native platform/runtime. The Xenia native-game target is evidence of a reusable packaging/platform route, not proof that ReXGlue output already builds or that the two game runtimes are ABI-compatible.
5. Adapt and test the Native Online rollback/session code against the chosen game runtime; verify update/version matching and actual online service compatibility. Do not claim Tekken 6 online, cross-play, or a working native game until the relevant console tests pass.

See `docs/PS5X360_REUSE_AND_RECOMP_INTEGRATION.md` for the source findings and integration plan, and `docs/PS5X360_COMPONENT_COMPATIBILITY_MATRIX.md` for the audited as-is / adapter-required / incompatible matrix. The matrix is based on the release-pinned native entry point, link script and memory adapter; it explicitly separates Xenia's guest runtime from the native ReXGlue target.

## Route selection

**Primary route: native PS5 homebrew title.** The deliverable must be a real title folder registered by ShadowMountPlus, not a Windows executable or a payload-only demo.

The target is the updated Native Online experience—not merely offline Tekken 6. The currently available source includes the 2.3.5-era rollback/session integration and practice tools. The 2.4.x release notes advertise group lobbies/live spectating and additional rollback/performance fixes, but these later changes are not present in the pinned public source. They remain explicit porting targets, not implemented features; porting them requires the corresponding public source changes or a lawful, technically verifiable implementation, plus compatible service protocol access.

## Work recorded

- `docs/NATIVE_PS5_HOMEBREW_PORT.md`: native-port strategy and phased milestones.
- `docs/NATIVE_PS5_SOURCE_AUDIT.md`: source-level portability findings.
- `docs/ONLINE_PORTABILITY_NOTES.md`: session, rollback and input reuse points.
- `docs/PS5_MENU_AND_SETTINGS_SPEC.md`: controller-first menu, settings and UI acceptance criteria.
- `docs/PS5_TITLE_PACKAGING_AND_BOOT.md`: native title folder, runtime, signing, ShadowMountPlus and firmware-specific validation requirements.
- `native/first_boot/main.c`: first-boot notification diagnostic source, explicitly not the game.
- `native/first_boot/sce_sys/param.json`: proposed title metadata for the diagnostic.
- `native/first_boot/make_icon.py`: deterministic icon generator.
- `native/first_boot/BUILD_STATUS.md`: build record and console test results.
- `ports/ggpo-posix/`: POSIX implementation of GGPO platform timing and polling plus compatibility helpers.
- `include/ps5_compat/`: initial host-side Win32/Winsock compatibility headers for game helper code.
- `tools/prepare_ps5_game_source.sh`: applies the POSIX GGPO overlay and adjusts the upstream CMake target/link setup for a PS5/FreeBSD cross-build.
- `.github/workflows/ggpo-posix-compile.yml`: compiles, links, and executes a host-side GGPO polling/clock smoke test.
- `.github/workflows/ggpo-ps5-cross-compile.yml`: builds the actual upstream GGPO static library using the pinned PS5 SDK/toolchain, compiles the initial deterministic/netplay game-side modules against the PS5 compatibility layer, and uploads the GGPO archive.
- `.github/workflows/ps5-compat-smoke.yml`: compiles and exercises the first Win32/Winsock compatibility headers.
- `.github/workflows/native-ps5-diagnostic.yml`: CI build/package route using the public ProsperoStore native-app build tooling pinned to commit `3290ee0d43c5e8ac49870e7c7e84639374a56bf1`.

## Current status — do not overstate

Two native diagnostic builds were produced by CI. The first crashed on the user's PS5 with SIGSYS. The second build (`5363436d28564d56f03e89c76a34391b0d2e4621`) has now been tested by the user: it remains on a black screen without an immediate crash. This confirms the diagnostic process can stay running in the user's current setup; it does **not** confirm rendering, controller support, audio, game integration, or firmware-wide compatibility.

The second diagnostic deliberately avoids sleep and returning from `main`, using a busy loop to isolate the earlier crash. Close it with the PS button; do not leave it running. Artifact run: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40035488841

**The full Tekken 6 Native Online game has not been built or booted yet. Progress since the previous status: the full upstream GGPO source set compiles and links on Linux with the POSIX overlay; its poll/clock smoke test passes; the same GGPO static library cross-compiles for the PS5 target using the pinned public PayloadSDK/toolchain; and the initial deterministic/session/netplay/resimulation/snapshot game-side modules now pass the PS5-target compile check. The compatibility-header, socket, POSIX GGPO, source-audit, and PS5 cross-compile workflows all pass on commit `3015eb22b753031dee9984c77c77a221bd09c7d6`. Evidence: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40055627819, https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40055627840, https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40055632108, and https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40055627849.

The next engineering phase is no longer the initial netplay compile: it is the native title's graphics/runtime boundary and the ReXGlue-generated game target. The green CI compile is only a compile check, not a linked game executable. First prove a visible PS5 graphics/input loop; then integrate the generated ReXGlue game target and native platform services, and only then build and boot the full title. The pinned public source checkout contains no generated Tekken game code or assets; those must be generated from a compatible user-owned USA/Europe Rev 1 Xbox 360 ISO. Preserve the upstream GGPO rollback/session code and port it rather than replacing it with a separate netcode implementation.

## Latest verified CI progress — 24 October 2026

The newest CI runs on commit `1c2f9dedb2abd9f51b47ae50b37fda54f3257322` confirm:
- **PS5X360 source-contract audit: PASS** — exact release-pinned entry point, memory wrappers, native title link recipe and platform patch markers verified. Run: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40062884908
- **Host GGPO POSIX compile/link/runtime smoke test: PASS** — the actual upstream GGPO source set builds and the POSIX polling/clock test executes. Run: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40062884870
- **PS5-target GGPO static-library cross-compile: PASS** — PS5 SDK/toolchain build completed and uploaded artifact `ggpo-posix-ps5-static-library` (SHA-256 `3f0d18ced3cf6186791fc91d77869bda2544e20337a0a21176dad5a5c2ccb784`). Run: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40062884867
- **ISO import preflight and socket portability checks: PASS** — these validate helper logic and portability, not game-code generation or online service access. Runs: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40062888409 and https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40062888372

These are real compile/test results and improve confidence in the rollback library and platform adaptation, but they are not a linked or booted Tekken 6 title. The highest-risk unresolved engineering work remains ReXGlue game-code generation/ABI integration and a native graphics/presentation path. The PS5 GGPO archive is a build artifact for further integration, not an installable game package.

## Latest graphics/input build checkpoint

- Latest attempted native graphics/input workflow before the current retry: [run 40060776596](https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40060776596), commit `e4bfc76f0ba688fa36a348fb40e9186b2693a299`. It passed host dependency installation, then RADV's Meson configuration failed because the host LLVM/SPIR-V translator development package was missing: `Dependency "LLVMSPIRVLib" not found`.
- Corrective commit: `7627239f20e0850dbd0a6c55b469b2ff5565211c` installed `libllvmspirvlib-18-dev` and `llvm-spirv-18`; this resolved the original `LLVMSPIRVLib` missing dependency. The next failure was `C++ shared or static library 'clangBasic' not found` during RADV Meson configuration. Follow-up fix commit: `2ac09fc63584180041f57c0d94343206f12a4f82` adds Ubuntu's `libclang-18-dev`; its success remains unverified until CI reaches and passes RADV configuration/build. ("Install LLVM SPIR-V development dependency for RADV build"). The native graphics/input workflow now installs Ubuntu 24.04's `libllvmspirvlib-18-dev` and `llvm-spirv-18`, matching the LLVM 18 host toolchain.
- Latest retry: [run 40062184218](https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40062184218), commit `2ac09fc63584180041f57c0d94343206f12a4f82`. The host dependencies and RADV bootstrap passed, and all 29 probe source objects compiled, but the final link failed: `no public SDK stub exports required symbol radv_EnumeratePhysicalDevices`. The Vulkan-template probe therefore still has no packaged title. This is a separate foundation blocker, and supports prioritizing the PS5X360 native-game link/runtime recipe instead of investing further in an unrelated template linker. Do not treat this fix as verified until RADV config/build passes.
- The workflow will then generate a separate `PPSA99874` title from the pinned PS5 Vulkan starter, build it, package it with SHA-256, and upload an artifact. The starter is a real Vulkan 3D sample with model animation, a settings overlay, and camera movement via the controller, but the generated title has not yet been built or tested on the user's console.
- This build retry is a graphics/input foundation only. The full Tekken 6 executable is still unbuilt; actual game-code generation requires the user's compatible game image locally, and console rendering/controller behavior must be physically verified.

## Unknown / blockers

- ReXGlue runtime and generated-game integration with the native app runtime is unverified; the game source has not yet been generated from the required user-owned ISO.
- Current successful PS5 CI builds compile the GGPO archive and selected game-side objects, but do not link a complete game executable or include a renderer. The next missing proof is a visible native graphics/input loop and then a renderer path that can replace/adapt the Xenos backend.
- The PS5 GGPO static library is cross-compiled, but the full Tekken executable and ReXGlue Xenos GPU plugin have not been built together or booted.
- Initial timer, WinSock startup, and debug/profiling compatibility shims exist; full game-side API coverage and controller/audio behavior are not yet validated. Console keyboard focus is intentionally treated as always focused and host keyboard input is disabled in the initial shim.
- The public source does not contain official lobby endpoint and pinned certificate configuration. Do not invent endpoints or bypass authentication/certificate checks.
- Official server/operator compatibility with a PS5 client is unverified.
- Source/release gap: the latest public source commit is 2.3.5, while the release page is at 2.4.2. The 2.4.0 group-lobby/spectating feature and 2.4.1/2.4.2 fixes cannot be assumed to exist in the source currently being cross-compiled.
- Cross-play with PC Native Online must be tested against the same compatible release/protocol; it cannot be promised from a successful build alone.

## Acceptance criteria

- Diagnostic title builds and launches from the home screen on the user's firmware 13.60 setup.
- Reproducible native PS5 build and launch instructions.
- No game image, extracted assets, generated game code, credentials, private certificates, or proprietary Sony modules bundled in the public repository.
- Correct controller input, audio, rendering, and stable gameplay timing.
- Existing rollback netplay preserved and tested.
- Updated online features implemented where their code and service protocol permit.
- Official matchmaking access only with legitimate configuration and verified compatibility.
- A cross-play test against the matching PC Native Online client passes before cross-play is described as working.


## Latest engineering progress — game/rollback adapter contract

Commit `ccb30d72612c92717506d58668f2e67789f78c74` adds `include/t6_game_runtime.h`, a stable boundary for the future generated-game adapter:
- A fixed-size, 16-byte per-frame input record so rollback can replay captured input instead of sampling the controller during resimulation.
- Explicit initialize/shutdown and deterministic one-frame advance callbacks.
- State-size/save/load callbacks for GGPO rollback snapshots, with the contract documenting that snapshots must include all simulation-affecting state and exclude device/socket/wall-clock state.
- A strict host CI smoke test uses a fake game to verify input delivery, snapshot save, further simulation, and restore.

Verification: [Game runtime adapter contract CI](https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40063168998) — compile and runtime test passed on Ubuntu 24.04. This validates the interface/test harness only; it does not mean the generated Tekken code has been adapted yet. The next step is to implement the adapter against actual ReXGlue-generated entry points and prove state determinism, then connect the callback surface to GGPO.


## Follow-up — rollback contract included in PS5-target compile checks

Commit `39bda158c26f2d43703278248660aaf9cc451464` wires the new game-runtime contract header into the existing PS5-target C++ header smoke test. The Prospero cross-compile job now checks the 16-byte frame-input ABI and compile-time callback contract on the PS5 toolchain as well as the host CI smoke test. [PS5 compatibility header workflow](https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40063318142)

This is still a boundary-validation milestone, not the game integration itself. The next critical task is implementing against the actual ReXGlue-generated game entry points and its existing snapshot machinery. Upstream `t6_snapshot.cpp` shows why this cannot be treated as a generic memory-copy callback: the existing snapshot path synchronizes worker threads and GPU/draw-idle state, and its memory walker relies on host-specific page queries. Those constraints must be preserved or deliberately replaced by a native renderer/runtime design before rollback can be trusted.

## Verified CI checkpoint — 24 October 2026

At commit `3229a0a94b684881c8eee7592da628d9c53c3d75`, the latest GitHub Actions runs have completed successfully:

- [GGPO PS5 cross-compile](https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40063332049) — PS5-target static library plus compatibility/game-side module compilation.
- [GGPO POSIX port compile test](https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40063332038) — host compile/link test.
- [PS5 compatibility header smoke test](https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40063332120).
- [Reference source audit](https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40063332094).
- [Game runtime adapter contract](https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40063335248).
- [Socket portability test](https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40063335176) and [ISO import preflight](https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40063335245).

These are successful source/compile/contract checks, not a complete game link or console gameplay test.

### Source-preparation and integration audit

Reviewed `tools/prepare_ps5_game_source.sh`, `tools/apply_ggpo_posix_overlay.sh`, `tests/ggpo-posix/CMakeLists.txt`, and the pinned PS5X360 v1.0.2 native entry/build recipe. The PS5 preparation script is already invoked by the cross-compile workflow, so adding a duplicate preparation workflow would not increase coverage. It currently patches platform selection, libc++ compatibility, snapshot page protection, crash handling and optional Windows-only diagnostics, while compiling the deterministic/netplay/resimulation/snapshot source modules.

The next real milestone is a **native shell link/package adapted from the pinned PS5X360 title recipe**, not another GGPO-only test. Its current entry point depends on Xenia's emulator, window/presenter, Xenos graphics and Xenia audio interfaces; those are not drop-in services for ReXGlue-generated native game code. The link recipe is a reference for SDK/RADV/Prospero packaging only. The port still needs a compatible native presentation/input/audio boundary and a generated-game adapter built from the user's own compatible Tekken 6 image.

Do not claim a playable port until a native title is linked, packaged, launched on the user's PS5, and shows a visible frame; controller/gameplay, audio, and rollback then need separate validation. Keep proprietary generated game sources and assets local.


## Latest checkpoint — runtime rollback contract hardening (24 October 2026)

- Commit `ee2ceebe4c89447944a599297cada60f63887872` strengthens the host runtime contract test: incomplete callback tables fail validation; snapshot restore plus identical captured-input replay must reproduce the same fake simulation state; invalid snapshot sizes and null buffers must be rejected. Host workflow passed: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40063901483
- Commits `8f104216a39588d2545b622a13b9e6ab46054edf` and `8ff3ae17286e030ae4f7ab9368e4c4f9602c8632` add a PS5-target object compile of that runtime contract test to the cross-compile workflow. This checks the test/API against the Prospero toolchain; it does not link a game executable. CI for this change is queued/running and must be checked before claiming it passed.
- The core blocker remains unchanged: this contract still uses a fake game. There is no generated Tekken 6 game implementation wired into `GameCallbacks`, no complete native title executable/package, and no console-tested renderer/input/audio integration. The next implementation gate is to get the actual compatible ReXGlue-generated source into a local, user-owned build workspace and define the renderer/platform adapter boundary before claiming game integration.


## Latest checkpoint — deterministic controller input capture (24 October 2026)

- Added `include/t6_input_adapter.h`. The platform pad layer now has a small, testable boundary for converting an already game-action-mapped pad sample into the fixed 16-byte per-frame input record. It normalizes 8-bit stick axes to signed 16-bit values, preserves trigger values/player index, and yields neutral input when disconnected.
- Extended `tests/game-runtime-contract.cpp` to test minimum/center/maximum axis values, trigger/button transfer, disconnected-controller neutrality, and the existing rollback restore/replay contract.
- The PS5-target CMake check already compiles this same test as an object target, so the new input boundary is included in the Prospero compile gate.
- Previous full PS5 cross-compile passed at `00d72b5cb3d0844a9f42ea76bdc3659edee84a41`: the GGPO archive and selected netplay/snapshot modules compiled, and the runtime-contract object target compiled successfully. [PS5 cross-compile run](https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40063960582)
- Current CI for the new input adapter is running/queued at commit `ece79e54f7d30ef29e79de5b8f6b911139c735ac`; check the runs before treating this change as verified.
- This is an input-boundary implementation only. The platform-specific DualSense poller must still translate the actual SDK state/buttons into `PadSample`; generated Tekken code, rendering, audio, native packaging and console gameplay are still not integrated.


## Latest checkpoint — expanded input edge cases and CI revalidation (24 October 2026)

- Commit `d044f6b1304ca4994e7edc300be75b09b635776d` extends the controller-input tests with values adjacent to stick center, proves a captured frame input remains unchanged when the sample is later modified, and verifies that disconnect neutralizes all four axes, both triggers, and buttons.
- On this commit, the runtime contract and PS5 compatibility header smoke tests passed. The full GGPO PS5 cross-compile also completed successfully: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40064219564
- The full cross-compile proves the GGPO archive and selected portable modules build for the pinned Prospero target. It does not prove that a native Tekken title links or launches.
- The prior graphics/input probe build is blocked at final link, not at C++ compilation: run https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40062184218 failed because the chosen public SDK stub set does not export `radv_EnumeratePhysicalDevices`. Do not report a successful graphics package from that run. The next renderer task is to resolve the exact import/link compatibility against the pinned runtime, or select a consistent, known-working PS5 title foundation; do not guess at or silently stub the missing Vulkan symbol.
- A separate public Prospero input backend has now been inspected for potential reuse: `prospero_input_driver.cpp` uses the native `scePad` lifecycle, maps the typed native pad state through `MapPadState`, handles disconnect/reconnect and errors, and avoids relying on raw byte offsets. Reuse is conditional on license and revision compatibility with the selected ReXGlue runtime.
- Current blockers: the renderer/title link route remains unresolved; the actual user-owned Tekken 6 source has not been generated and integrated; no complete native Tekken executable/package exists; and the current native diagnostic is only a process-liveness test. The game is not yet bootable.


## Latest checkpoint — revalidated PS5 components and renderer retry (24 October 2026)

- Commit `2984e4e8a7250dfbc0d59901e93e9848600fd289` records the native renderer import/link blocker and the typed ReXGlue Prospero pad backend candidate.
- On that commit, the game-runtime adapter contract, ISO import preflight tests, socket portability tests, GGPO POSIX compile test, PS5 compatibility header smoke test, GGPO PS5 cross-compile, and reference-source audit all passed. Links:
  - GGPO PS5 cross-compile: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40064368333
  - PS5 compatibility header: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40064368422
  - POSIX compile: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40064368461
  - Reference audit: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40064368316
- A fresh rebuild of the pinned PS5 graphics/runtime stack is now running at https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40064368326; at this checkpoint it is still in the bootstrap stage, so no renderer artifact is claimed.
- This work remains component-level. A bootable native Tekken 6 title still requires the renderer/title link route to succeed, user-owned generated game source to be integrated locally, and console validation. No copyrighted game source or assets are committed to the public repository.


## Fresh native renderer attempt — 24 October 2026

The second graphics/input probe attempt reached the native title linker: all 29 C/C++ compilation steps completed, but packaging was skipped because linking failed again with `error: no public SDK stub exports required symbol radv_EnumeratePhysicalDevices`. Run: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40064368326.

This confirms the earlier failure is reproducible and isolated to native linking/import validation rather than compilation. Do not add a dummy Vulkan symbol or call this a successful title. The next engineering step is to inspect the pinned native tool's import validation and ensure the RADV archive, title template, Payload SDK fork, and PS5_Vulkan link recipe are a compatible set at fixed revisions. Current public PS5_Vulkan's own RADV link recipe whole-archives its Mesa driver and binds platform libc symbols locally; use that as a consistency reference, not as proof that simply changing a URL fixes the mismatch.

Core GGPO, PS5 compatibility-header, source-audit and preflight checks remain passing, but there is still no packaged renderer probe and no generated Tekken game executable. Game source/data and game-specific renderer/runtime integration remain separate required milestones.


## Latest build-pipeline hardening — 24 October 2026

- Commits `bb9f88e9e860d735366faadb750237d64de9ec4b`, `e45af04b83c95e4eaba629d2e9ad26da0c2e7067`, `ad803c228e7d7fe48320efb5e9affbc8b6d6e933`, and `6d5d1b864490612a855c5973072efe394ed6d4b3` extract the LLVM 18 RADV link workaround into `tools/patch_radv_linker.py`, add unit tests, and use the tested helper in both native graphics workflows.
- The patch helper is intentionally fail-closed: it only changes exactly one known linker command, tolerates an already-patched command on retries, and rejects unexpected or duplicate command layouts. Each graphics workflow runs the helper's unit tests before proceeding to title linking.
- Source was re-read after commits to verify the helper, tests, and both workflow call sites are present. The current GitHub commit-status endpoint returned no status entries for the latest workflow commits, so no new successful CI run or artifact is claimed yet.
- This is build-system hardening only. The RADV import/link issue still needs a successful run to prove the fix works with the pinned toolchain. No complete Tekken 6 game runtime has been linked, and no playable package or PS5 gameplay test exists yet.
