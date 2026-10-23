# Native PS5 Homebrew Port Strategy

**Primary target:** a native PS5 homebrew title that appears on the PS5 home screen through ShadowMountPlus, with the updated Tekken 6 Native Online features preserved wherever technically possible.

This is a feasibility and build effort, not a claim that the game already runs on PS5.

## Why native is the right direction

ProsperoStore is a catalog/installer for PS5 homebrew apps; it does not automatically convert Windows games into PS5 apps. A Tekken port needs a native executable, valid title metadata, a compatible runtime, a correct title folder, and a launch path that works on the user's firmware.

The upstream Native Online project is a Windows PC static recompilation of the Xbox 360 game. Its builder translates the user's own compatible game image to generated C++ and compiles it for Windows. The current game build uses a Xenos graphics plugin, Windows socket/timer libraries, Windows GUI startup, and other platform-specific integrations.

## Current native title route

The project now has a first-boot diagnostic source and a CI recipe in .github/workflows/native-ps5-diagnostic.yml. The workflow uses public ProsperoStore native-app build tooling pinned to a specific commit, including its reproducible clean-room runtime build, to produce a folder ZIP. This diagnostic is intentionally tiny: it sends a system notification and exits after a short delay.

The diagnostic is only a tooling/packaging milestone. Its build must pass, and it must be launched from the PS5 home screen on firmware 13.60 before we can call the install route proven. A CI-built ZIP is not proof of console compatibility.

See:
- [First-boot diagnostic source](../native/first_boot/README.md)
- [Title packaging and boot requirements](PS5_TITLE_PACKAGING_AND_BOOT.md)
- [Current status](../PORTING_STATUS.md)

## Reuse versus replace

### Reuse where portable
- ReXGlue-generated game logic after it can be compiled for the PS5 target.
- GGPO rollback/netplay logic, subject to portability and deterministic timing checks.
- Game-specific patches and simulation behavior, where they do not depend on Windows APIs.

### Replace or port for PS5
- Windows/Win32 host APIs and process lifecycle.
- The Xenos graphics backend and DirectX 12/DXGI/D3D dependencies with a PS5 graphics backend.
- Audio and controller input integration.
- Memory allocation, threading/synchronization, timers, file paths, and socket integration as needed.
- The Qt launcher: initially replace it with a small native homebrew front end or a minimal direct-launch test harness.
- Windows-only build scripts and compiler assumptions.

Do not assume this is a simple recompile. The graphics backend and OS interfaces are the largest unknowns.

## Milestones

1. **Native title boot proof.** Build a diagnostic title with metadata and a reproducible runtime, register it with ShadowMountPlus, and launch on firmware 13.60.
2. **Audit the game portability boundary.** Map platform-specific includes, DirectX types, Win32 calls, input/audio dependencies, and build assumptions in upstream source.
3. **Port a tiny host layer.** Add a PS5 platform target with logging, clock/timing, files, memory, threads, and controller input. Keep the Windows target working.
4. **Graphics spike.** Render a test frame through the PS5 graphics API before attempting the full game renderer. Do not promise performance until measured.
5. **Compile the recompiled game logic.** Resolve compiler/ABI and generated-code issues without changing game behavior unnecessarily.
6. **Audio/input and local boot.** Reach a stable offline match at target frame rate, test controller mappings and sound.
7. **Online compatibility.** Preserve the GGPO protocol and game simulation. Verify legitimate service access and a match with a PC player only after a native offline build works.

## Online constraint

A native build does not itself solve matchmaking. The public source says official server configuration and its pinned certificate are not published. Do not invent endpoints, bypass certificate checks, or assume that the official PC service permits another client. Online compatibility is a separate milestone requiring legitimate service configuration and protocol testing.

## Distribution and game files

- Keep copyrighted game images, extracted assets, generated game code, credentials, private certificates, and server secrets out of this public repository and its public CI artifacts.
- Distribute only the homebrew port code and legally distributable components. Users should supply their own compatible game copy.
- ProsperoStore catalog listing is a later step after the app is functional, packaged correctly, and meets catalog requirements.

## Current status

A diagnostic source and automated package build are committed. The first CI attempts exposed a missing optional build tool (ccache); the workflow was updated to install Ninja and disable the optional cache. The newest build run is in progress. Neither a passing build nor a console launch on firmware 13.60 has been confirmed yet.
