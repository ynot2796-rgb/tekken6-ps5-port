# ReXGlue runtime entry-point audit

**Pinned source:** ReXGlue SDK `f5337cdc947ff6d4c4196737e2c807a48f2a1fc2`  
**Purpose:** record the real runtime API before writing a PS5 title entry point.  
**Status:** source API inspected; no PS5 title has linked against this runtime yet.

## Verified runtime API

The public header is `include/rex/runtime.h`. The entry point is the `rex::Runtime` class, not a guessed C function or a generic `ReXApp` launcher.

- Construct `rex::Runtime` with game-data, user-data, update-data, cache and optional metadata roots.
- Populate `rex::RuntimeConfig` with injected platform services:
  - `graphics`: an implementation of `rex::system::IGraphicsSystem`, or leave empty for no guest GPU.
  - `audio_factory`: factory for an `IAudioSystem` after the runtime creates its function dispatcher.
  - `input_factory`: factory for an `IInputSystem`.
  - `kernel_init`: optional kernel service initialization callback.
  - `tool_mode`: true explicitly skips guest GPU initialization and is intended for analysis tools.
- Call `Runtime::Setup(RuntimeConfig)` for subsystem setup only.
- For a generated game image, call `Runtime::Setup(const PPCImageInfo&, RuntimeConfig)`; this additionally initializes the per-module function dispatch table and registers generated `PPCFuncMapping` entries.
- Load the game XEX with `LoadXexImage`, then start it with `LaunchModule` (or prepare a suspended thread with `PrepareModuleLaunch`).
- Call `Shutdown()` before destroying the runtime; the destructor also calls shutdown.

## Important integration consequences

1. A real Tekken launch requires a valid generated `PPCImageInfo` and its function mappings. A plain `Runtime::Setup` smoke test is not game execution.
2. The runtime does not provide the PS5 graphics, input or audio implementations automatically. Those are injected through `RuntimeConfig`.
3. `RuntimeConfig::graphics` can be omitted for a headless/tool runtime, but the Tekken Xenos path requires a compatible Xenos graphics backend and native presentation integration.
4. The runtime owns the guest memory, virtual filesystem, kernel state, dispatcher and export resolver after setup. Do not create duplicate global instances.
5. The Xenos renderer is not a standalone title renderer: it is a guest-GPU plugin and depends on the runtime's GPU interfaces and native presentation path.
6. Both `rexruntime` and `rexgpu-xenos` are declared `SHARED` in their CMake target definitions. Do not plan to statically link both into the EBOOT merely because the current workflow artifact glob is `*.a`; inspect the real generated filenames and build-tree metadata first.
7. The Xenos plugin is explicitly runtime-loaded, not linked by consumers. `include/rex/system/gpu_plugin.h` defines `rex::system::LoadGpuPlugin(name, backend)`, the ABI version, and the exported factory symbols. `src/system/gpu_plugin_loader.cpp` loads `librexgpu-xenos.so` from the executable's directory on non-Windows platforms, validates `rex_gpu_abi_version` and `rex_gpu_create`, and returns an `IGraphicsSystem`. The title must stage the matching plugin beside the executable and pass the returned graphics system into `RuntimeConfig::graphics`.
8. The plugin CMake target links privately against `rexruntime`; its CMake comment explicitly says consumers never link the plugin target and that runtime-loaded plugin binaries are expected. Keep the plugin and runtime ABI-compatible and build them from the same pinned SDK/configuration.

## Current build gate

The pinned ReXGlue runtime and Xenos Vulkan target have compiled successfully on the earlier build run. The latest run is still compiling. The next inventory stage records archive members and undefined symbols; it must be inspected before creating a title linker command.

## Next implementation sequence

1. Finish the current native archive/symbol inventory.
2. Identify the actual output types, link interfaces and platform imports from the generated build tree.
3. Build a minimal PS5 executable that constructs and sets up ReXGlue in a controlled mode, using only verified PS5-compatible dependencies.
4. Add native input/audio/presentation implementations through the documented `RuntimeConfig` injection points.
5. Add the locally generated Tekken `PPCImageInfo`, function mappings and XEX data path.
6. Validate module load, first frame, input, audio and shutdown on the user's firmware 13.60 console.

No generated Tekken source, proprietary game asset, game image, Sony runtime module or private credential is part of this audit.
