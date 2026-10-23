# Native PS5 Title Packaging and First-Boot Plan

Status: researched requirements and source review; **no console-tested artifact yet**.

## Why a proper native title is the target

ProsperoStore apps are native PS5 titles. The relevant public routes reviewed are:
- `Rufidj/ps5link-sdk`: builds real title executables from `prospero-clang` objects and provides a native linker.
- `darkxex/ProsperoStore`: uses a native-app boilerplate, app metadata, a runtime, packaging and a ShadowMountPlus folder install.
- `PSBrew/ShadowMountPlus`: the folder registration/auto-mount layer.

A payload ELF sent to TCP port 9021 is not the same thing as a home-screen app. We need a title folder with a valid `eboot.bin` and metadata, and we must validate the runtime module and signing approach for the target firmware.

## Typical folder structure

The public ps5link SDK documents a real title folder similar to:

```text
PPSAxxxxx/
  eboot.bin
  sce_module/
    libc.prx
  sce_sys/
    param.json
    icon0.png
```

Important constraints:
- The title ID must be unique and match the metadata.
- The signed executable must be produced from the current build, not a stale ELF.
- The ps5link SDK documentation says `sce_module/libc.prx` is required and must be a signed module compatible with the console firmware. It is a Sony-owned component and must not be distributed by this repository.
- Therefore a complete ZIP cannot honestly be called install-ready unless its runtime dependency is legally and correctly supplied.
- ShadowMountPlus needs to scan the chosen install folder; its version/configuration matters.

## Firmware 13.60 is a required test target

The ps5link SDK README reports testing on firmware 9.00 and warns that other firmware is untested. That is not enough evidence to claim compatibility with 13.60. Current ProsperoStore documentation says other firmware support has historically been experimental and notes ShadowMountPlus plus an ELF loader on TCP 9021 for its helper workflows. Do not copy old instructions blindly; test the user's actual ShadowMountPlus version and setup.

The release checklist must include:
1. Build the native title from a clean checkout with pinned dependencies.
2. Verify output file existence, title metadata, expected imports and runtime requirements.
3. Produce a ZIP containing only files that can lawfully be distributed; document any locally supplied runtime dependency.
4. Verify ZIP layout so the title folder is at the correct depth.
5. Copy to the configured ShadowMountPlus scan path, register, launch, and capture console/kernel logs.
6. Repeat on firmware 13.60; a build or test on another firmware does not count.
7. Do not report success until the title actually launches from the PS5 home screen.

## First artifact before the game

The first console artifact should be a small native diagnostic title (notification and/or controller input proof), not a fake Tekken launcher. It should verify the build/sign/packaging route and the exact PS5 firmware before game-engine work begins.

This diagnostic title does not meet the user's final goal. The final goal remains a native Tekken 6 Native Online app with rollback and updated online functionality.

## Tekken-specific blockers

- The upstream game is currently configured for Windows, with a Xenos GPU plugin and Windows socket/timer libraries.
- The ReXGlue game/runtime and GGPO session/snapshot integration must be ported and tested.
- Controller input must translate DualSense state to the game input model deterministically.
- Audio, rendering, timing, threads, filesystem and sockets need native implementations.
- Official lobby/server endpoint and pinned-certificate configuration are absent from the public upstream source. Matchmaking and cross-play cannot be promised until legitimate service configuration and protocol compatibility are established.
- User-owned compatible game files and generated game data must remain local; do not bundle them in public builds.

## Build artifact honesty

A CI build that produces an ELF, a signed executable, or even a folder ZIP is only a build milestone. It is not a working PS5 file until all runtime requirements are present and the title has launched on firmware 13.60. No Sony runtime module, game ISO, extracted game assets, private certificate, or server secret will be bundled in this repository.
