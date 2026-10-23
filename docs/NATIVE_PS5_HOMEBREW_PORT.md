# Native PS5 Homebrew Port Strategy

**Preferred long-term target:** a native PS5 homebrew build that installs/launches as a PS5 application, rather than running the Windows release through MihawkOS or Prospero Win.

This is a feasibility plan, not a claim that a PS5 build exists.

## Why native is the right direction

ProsperoStore is a catalog/installer for PS5 homebrew apps; it does not automatically convert Windows games into PS5 apps. A Tekken port would need a PS5-native executable and a compatible package/launch path before it could be listed there.

The upstream Native Online project is a Windows PC static recompilation of the Xbox 360 game. Its builder translates the user's own compatible game image to generated C++ and compiles it for Windows. The Windows launcher uses Qt/Win32 and the current game runtime has platform-specific graphics, input, audio, memory, threading, and networking boundaries.

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

1. **Audit the portability boundary.** Map platform-specific includes, DirectX types, Win32 calls, SDL/input/audio dependencies, and build assumptions in upstream source.
2. **Prove the PS5 toolchain.** Build a minimal PS5 homebrew ELF using the public PS5 Payload SDK/toolchain and run it on the target firmware using the user's established homebrew launch method.
3. **Port a tiny host layer.** Add a PS5 platform target with logging, clock/timing, files, memory, threads, and controller input. Keep the Windows target working.
4. **Graphics spike.** Render a test frame through the PS5 graphics API before attempting the full game renderer. Do not promise performance until measured.
5. **Compile the recompiled game logic.** Resolve compiler/ABI and generated-code issues without changing game behavior unnecessarily.
6. **Audio/input and local boot.** Reach a stable offline match at target frame rate, test controller mappings and sound.
7. **Online compatibility.** Preserve the GGPO protocol and game simulation. Verify server access and a match with a PC player only after a native offline build works.

## Online constraint

A native build does not itself solve matchmaking. The public source says official server configuration and its pinned certificate are not published. Do not invent endpoints, bypass certificate checks, or assume that the official PC service permits another client. Online compatibility is a separate milestone requiring legitimate service configuration and protocol testing.

## Distribution and game files

- Keep copyrighted game images, extracted assets, generated game code, credentials, and server secrets out of this public repository and its public CI artifacts.
- Distribute only the homebrew loader/port code and legally distributable components. Users should supply their own compatible game copy.
- ProsperoStore listing would be a later distribution step after the app is demonstrably functional, packaged correctly, and compliant with catalog requirements.

## Current status

No native PS5 executable exists yet. The current repository is a planning/scaffold project. The next useful engineering step is a source portability audit and a minimal PS5 SDK build proof—not spending more time on the Windows launcher build as if it were the final target.
