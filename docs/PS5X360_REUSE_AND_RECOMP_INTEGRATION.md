# PS5X360 reuse and Tekken 6 recompile integration

**Purpose:** Preserve the actual goal—a native PS5 Tekken 6 port with the updated game and online functionality—while reusing proven PS5/Xenia platform code to avoid rebuilding the graphics/runtime layer unnecessarily.

## Source baseline

- Repository: https://github.com/BrinooTk/PS5X360
- Latest release inspected: [v1.0.2](https://github.com/BrinooTk/PS5X360/releases/tag/v1.0.2)
- Release commit: `0a178708ea2138413eea60eb7625496457455137`
- Matching source archive: `PS5X360-source-1.0.2-changes.zip` attached to the v1.0.2 release.
- Project license: MIT. Preserve the notices and comply with each bundled component's separate license (including the Vulkan/Mesa runtime, Xenia, and netplay dependencies).

The source should be audited from the release-matched archive and compared with the default branch. Do not assume current main exactly reproduces the released binary.

## Reuse candidates confirmed from the repository

1. **Native title build/package route:** `tools/build-native-game.sh` builds the PS5-native Xenia game target, links Xenia core libraries and the RADV/Mesa stack, creates the PS5 SELF/title layout, and packages it. This is a valuable implementation reference for a native PS5 executable.
2. **PS5 platform adaptations:** `patches/canary/xbox360ps5.patch` documents Prospero-specific source selection and changes for clock timing, executable/user paths, and logging. The broader platform tree includes native memory/fault-handling, filesystem, network logging, and runtime glue.
3. **Graphics:** PS5X360 uses its PS5 Vulkan/RADV stack. Reuse its pinned build/link integration where technically compatible; don't mix unrelated Mesa revisions, SDKs, or linker scripts.
4. **Input/audio:** audit the exact release source and native runtime adapters for reusable `scePad`/DualSense and `sceAudioOut` code. Map them to the interfaces expected by generated Tekken code.
5. **Updates and per-title configuration:** use PS5X360's version-matching and content-installation logic as a reference for identifying the correct game build/update. Do not blindly apply an update to a mismatched executable revision.
6. **Networking:** v1.0.2 improves Xenia netplay requests and records some PS5 console checks, but its release notes explicitly say a complete joined multiplayer match was not yet confirmed. Tekken 6's Xbox LIVE compatibility and the Native Online protocol remain separate verification tasks.

## Integration boundary

PS5X360 is an Xbox 360 emulator. Its existing Xenia title can run Xbox 360 code through Xenia's guest CPU/GPU/runtime. The target here is a **native recompiled Tekken 6 executable** using ReXGlue plus the Native Online game-side integration. Therefore:

- Reuse platform-level pieces (PS5 title lifecycle, native runtime startup, memory, timing, logging, Vulkan/RADV linking, input/audio service adapters) where interfaces and licenses allow.
- Do not assume the Xenia guest runtime, guest memory model, or emulator-specific GPU command pipeline can simply be linked into the recompiled game. Keep the game's own generated-code ABI and renderer requirements explicit.
- Preserve the GGPO rollback/session integration from the pinned Native Online source and adapt its platform dependencies rather than replacing it with unrelated netcode.
- Keep user-owned game images, generated proprietary game code/assets, credentials, and private certificates out of the public repository.

## Execution order

1. Inspect the release-matched v1.0.2 source archive and extract the exact PS5 platform/runtime interfaces and build pins.
2. Make a component map against the current Tekken port: reusable as-is, needs adapter, incompatible, or still unknown.
3. Update the native-port build to reuse compatible PS5 title/runtime infrastructure before expanding the separate graphics probe. Retain the probe as a fallback for isolated rendering/input validation.
4. Generate the Tekken game code from a compatible user-owned game image and compile/link the first native game target.
5. Integrate graphics, input, audio, deterministic timing, and GGPO rollback/session code; build and boot a real title.
6. Validate game-update matching, online sign-in/matchmaking, joining a match, and cross-play separately on the user's console. Never claim success from compile-only CI.

## Evidence and limits

- PS5X360 repository: https://github.com/BrinooTk/PS5X360
- v1.0.2 release notes/source assets: https://github.com/BrinooTk/PS5X360/releases/tag/v1.0.2
- Native Tekken source pinned in `PORTING_STATUS.md`: Native Online public source v2.3.5 era; the later v2.4.x release features are not assumed present in that pinned source.
- At this checkpoint, no complete native Tekken 6 executable has been linked or booted. The reuse plan is now recorded; implementation and physical-console proof remain outstanding.
