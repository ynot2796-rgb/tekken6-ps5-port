# Tekken 6 Native Online — Native PS5 Port

**Status: native diagnostic launch verified; Tekken 6 itself is not ported yet.** The user reports the diagnostic title stays on a black screen without an immediate crash on their PS5 setup. The upstream GGPO library has also cross-compiled successfully in an earlier CI run, and host-side portability tests pass. None of this is a playable game build.

## Goal

Build a **native PS5 homebrew title** for Tekken 6 Native Online, preserving its existing GGPO rollback/netplay and updated online features where the platform and service dependencies permit. The final target is a home-screen app registered by ShadowMountPlus, like native apps distributed through ProsperoStore—not a Windows `.exe`, a renamed file, or a payload-only demo.

## Native PS5 route

The chosen route is a real native title build:
- Evaluate the public [ps5link SDK](https://github.com/Rufidj/ps5link-sdk) and [PS5 payload SDK](https://github.com/ps5-payload-dev/sdk) for toolchain, linker and platform interfaces.
- Follow the native-title structure and packaging requirements documented in [PS5 title packaging and boot](docs/PS5_TITLE_PACKAGING_AND_BOOT.md).
- A first-boot diagnostic title ZIP was built and launched through the user's ShadowMountPlus setup on firmware 13.60. The black screen is expected for this process-liveness test; see [build record and install test](native/first_boot/BUILD_STATUS.md).
- Only after that proof, port the game runtime, rendering, input, audio, timing, filesystem and networking dependencies.
- Preserve upstream rollback/session/snapshot behavior and validate PC cross-play against the matching upstream version before claiming it works.

## Research and port notes

- [Native PS5 homebrew port plan](docs/NATIVE_PS5_HOMEBREW_PORT.md)
- [Source portability audit](docs/NATIVE_PS5_SOURCE_AUDIT.md)
- [Online portability notes](docs/ONLINE_PORTABILITY_NOTES.md)
- [PS5 title packaging and boot requirements](docs/PS5_TITLE_PACKAGING_AND_BOOT.md)
- [First-boot diagnostic build record](native/first_boot/BUILD_STATUS.md)
- [Current porting status and blockers](PORTING_STATUS.md)

## Upstream

- Native Online source: https://github.com/Ekspym/tekken6-native-online-source
- Native Online releases: https://github.com/Ekspym/Tekken6-native-online/releases
- ReXGlue SDK: https://github.com/rexglue/rexglue-sdk
- Original recompilation work: https://github.com/mahmoud-mess/tekken6-recomp
- Native title linker/SDK: https://github.com/Rufidj/ps5link-sdk
- ShadowMountPlus: https://github.com/drakmor/ShadowMountPlus
- ProsperoStore: https://github.com/darkxex/ProsperoStore

## Important technical facts

The upstream build is Windows-oriented: it links a GGPO fork against Windows socket/timing libraries, uses the Xenos GPU plugin, has Windows GUI startup configuration, and applies CPU/compiler flags that need review for the PS5 toolchain. Its source has reusable session, rollback, snapshot and controller integration, but those do not become PS5-compatible merely by recompiling.

The public upstream source README says the official lobby endpoint and pinned certificate configuration are not published. Official matchmaking and cross-play are therefore open issues, not guaranteed features.

A native title folder commonly contains `eboot.bin`, `sce_sys/param.json`, an icon and required runtime files. The ps5link SDK documents a required signed `sce_module/libc.prx` compatible with the target firmware and states that this Sony-owned module cannot be distributed. A build artifact must not be called install-ready until its runtime requirements are handled correctly and it has actually launched on the user's firmware.

## Firmware target and honest status

Target console: jailbroken PS5 firmware **13.60**. Some public SDK projects document tests on older firmware only, so 13.60 compatibility must be tested directly. ShadowMountPlus registration is not the same as successful launch.

No game image, extracted game assets, generated proprietary game code, credentials, private certificates, server secrets, or Sony runtime modules are included in this repository.

## Milestones

1. [x] Toolchain and public reference-source revisions pinned in CI.
2. [x] Minimal native diagnostic title built and packaged by CI.
3. [x] Diagnostic title launched on the user's PS5 setup; black-screen/no-crash is only a process-liveness result.
4. [x] GGPO POSIX overlay passes host-side smoke tests; the GGPO static library has cross-compiled for PS5 in an earlier successful run.
5. [ ] Finish current CI validation of the PS5 compatibility headers and deterministic/netplay game modules.
6. [ ] Native graphics proof, then game runtime/ReXGlue integration and actual game build.
7. [ ] Offline gameplay, controller/audio, stable timing, rollback and performance tests.
8. [ ] Legitimate online-service configuration and a cross-play test against the matching PC release.
