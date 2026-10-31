# ReXGlue runtime entry-point audit

**Pinned source:** ReXGlue SDK `f5337cdc947ff6d4c4196737e2c807a48f2a1fc2`  
**Purpose:** record the real runtime API and PS5-specific linking contract before writing the Tekken title entry point.  
**Status:** runtime and Xenos Vulkan static archives compile on the pinned PS5 toolchain; PS5 static-factory loading correction is committed and under CI validation. No Tekken title ELF has linked or booted yet.

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

## Verified PS5 linking and GPU factory contract

The upstream SDK declares both `rexruntime` and `rexgpu-xenos` as shared targets for desktop platforms. The pinned PS5 patch deliberately changes both to **static** libraries because the installed title is linked into one native executable and must not depend on loading a separate plugin shared object.

The current successful compile workflow confirms the resulting files are static archives:
- `librexruntime.a` (22,884,098 bytes in run 41145204181)
- `librexgpu-xenos.a` (8,317,956 bytes in run 41145204181)

This is intentional, but it exposed a mismatch: upstream `src/system/gpu_plugin_loader.cpp` always used `DynamicLibrary::Load` and expected `librexgpu-xenos.so`. That desktop path cannot work with the PS5 static-archive packaging model.

**Correction committed:** the PS5 patch now has a platform-specific branch in `gpu_plugin_loader.cpp` that:
1. Accepts the linked `xenos` plugin only.
2. Calls the statically linked `rex_gpu_abi_version()` and checks it against `kGpuPluginAbiVersion`.
3. Builds the same `GpuCreateInfo` structure and invokes `rex_gpu_create()`.
4. Returns the created `IGraphicsSystem` without attempting `dlopen` or looking for a sidecar `.so`.

Desktop builds retain the original dynamic loader. The PS5 link must include both static archives, and the archive link order / whole-archive policy must ensure the plugin factory object is retained. The new change is being checked by the full compile workflow; the successful archive build alone does not yet prove the final ELF link.

## Important integration consequences

1. A real Tekken launch requires a valid generated `PPCImageInfo` and its function mappings. A plain `Runtime::Setup` smoke test is not game execution.
2. The runtime does not provide the PS5 graphics, input or audio implementations automatically. Those are injected through `RuntimeConfig`.
3. `RuntimeConfig::graphics` can be populated by `LoadGpuPlugin("xenos", "vulkan")`; on PS5 this now resolves the statically linked factory, not a plugin file.
4. The runtime owns the guest memory, virtual filesystem, kernel state, dispatcher and export resolver after setup. Do not create duplicate global instances.
5. The Xenos renderer is a guest-GPU implementation and depends on the runtime's GPU interfaces and native presentation path.
6. The PS5 graphics patch routes Vulkan entry points to the statically linked RADV ICD and uses `VK_KHR_display` for native display presentation. This still needs on-console validation.
7. The PS5 reference builder uses a dedicated `_start` CRT, constructor/finalizer sequencing, an explicit `application_main` symbol, and a custom Prospero linker adapter. Its startup source is a reference to adapt carefully, not a drop-in replacement: title identity, state paths, diagnostics and SDK-specific imports must be set for Tekken.
8. Keep runtime and Xenos archives ABI-compatible by building them from the same pinned SDK revision and configuration.

## Current build gate

- Run `41145204181` at commit `2f87f2141a7ab73dae76802a55a64f1c3ebd05f7` completed successfully, including archive inventory and symbol extraction.
- Artifact `13021406064` contains build diagnostics, the generated Ninja build, static archives and symbol reports.
- Commit `747538b2f2d97846945bd70dc9a40d69a8504516` adds the PS5 static-factory loader correction. CI is currently validating that patch against the pinned SDK.
- The next gate is not another library-only smoke test: it is a minimal PS5 executable link using the dedicated CRT/link adapter, both static archives, the static RADV ICD and a controlled ReXGlue setup path.

## Next implementation sequence

1. Complete CI validation of the PS5 static-factory patch.
2. Build a minimal native PS5 executable using the reference CRT/link adapter, with a correct Tekken title identity and controlled filesystem roots.
3. Verify that the final ELF contains the expected `_start`, ReXGlue runtime symbols, Xenos factory symbols and statically linked Vulkan ICD entry point; inspect imports and unresolved symbols.
4. Add native input and audio implementations through the documented `RuntimeConfig` injection points.
5. Add the locally generated Tekken `PPCImageInfo`, function mappings and XEX data path without publishing proprietary game data.
6. Validate module load, first frame, input, audio and shutdown on the user's firmware 13.60 console.

No generated Tekken source, proprietary game asset, game image, Sony runtime module or private credential is part of this audit.
