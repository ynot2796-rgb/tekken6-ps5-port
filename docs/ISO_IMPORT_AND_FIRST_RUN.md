# ISO import and first-run contract

## User-facing requirement

The released PS5 homebrew title must not require the user to run command-line tools, manually extract files, patch game code, or assemble developer dependencies. The user supplies their own compatible Tekken 6 Xbox 360 ISO through the app; the app performs every supported preparation step automatically and then launches the native title.

This is a release acceptance requirement, not a claim that the current diagnostic build supports ISO import.

## Compatibility baseline

The upstream Native Online source documents a user-owned **USA or Europe, Rev 1, Xbox 360** copy as its build input. Other regions/revisions must be rejected with a clear compatibility message until explicitly tested. Do not silently accept an image based only on its filename.

## Required first-run flow

1. **Select source** — provide a controller-friendly file picker for console storage and removable media. Never upload the ISO or extracted game data.
2. **Inspect and identify** — read the image format and disc metadata; determine whether it is a supported region/revision. Fail closed on ambiguous, malformed, encrypted/unreadable, or unsupported images and explain the next action.
3. **Prepare locally** — run the supported extraction and game-data preparation path without changing the source ISO. Use a staging directory, validate paths against traversal/symlink attacks, check free space, and preserve the user's existing saves/settings.
4. **Generate or locate runtime code** — this is a hard architecture gate. Native Online's documented PC build translates `Default.xex` to C++ and compiles it. The PS5 project must prove a lawful, practical strategy for making the matching generated game code available without asking the user to operate developer tools. Options must be evaluated and tested; do not assume generated game code is present in the public source or promise that a console-side compiler works before demonstrating it.
5. **Validate and commit install** — verify required game data, generated-code/runtime version compatibility, and required files before atomically promoting the staged install. On failure, keep the source untouched and show a recoverable error.
6. **Launch** — start the native PS5 runtime and show actionable diagnostics if initialization fails. Cache successfully prepared data so the ISO does not need to be processed again on every launch.

## Acceptance tests

- Supported ISO is identified correctly; unsupported region/revision and corrupt images are rejected with readable messages.
- Original ISO remains unchanged; no game data is uploaded or committed to this repository.
- Interrupted preparation can resume or safely restart without corrupting an existing install.
- Low storage, missing files, and failed code generation produce clear errors rather than a black screen.
- A completed install launches into visible native graphics, accepts DualSense input, and reaches gameplay before online features are marked ready.
- The user-facing path consists of selecting the ISO and following in-app progress; no PC, terminal, manual patching, or separate developer package is required for the intended release.

## Current blockers

- The current PS5 diagnostic is not an ISO installer or game.
- The public Native Online source does not include generated Tekken game code or game data.
- No end-to-end ISO identification, extraction, code-generation, native rendering, or gameplay path has been demonstrated on the target PS5.
- The upstream PC source snapshot is 2.3.5-era while the separate release repository has 2.4.x releases; those newer features remain unverified porting targets.

## Implementation order

1. Prototype and test the ISO identification/data-preparation path against a user-owned compatible image, without committing or uploading its contents.
2. Decide the generated-code strategy using measurements and the existing ReXGlue builder pipeline; this must be solved before claiming the ISO-only experience is feasible.
3. Bring up a visible native graphics/controller loop on firmware 13.60.
4. Integrate the generated game target, Xenos-to-native graphics path, audio, and existing GGPO/session code.
5. Add the controller-first installer/launcher UI and test fresh install, restart, failure recovery, offline gameplay, then online compatibility.
