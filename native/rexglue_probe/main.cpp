#include <filesystem>
#include <memory>

#include <rex/runtime.h>
#include <rex/system/gpu_plugin.h>

// Native runtime/plugin smoke entry point only. It does not load Tekken's XEX
// or generated PPC mappings and must not be described as a game boot.
int main() {
  const std::filesystem::path root = ".";
  std::filesystem::create_directories(root / "savedata");
  std::filesystem::create_directories(root / "cache");

  auto graphics = rex::system::LoadGpuPlugin("xenos", "vulkan");
  if (!graphics) {
    return 10;
  }

  rex::Runtime runtime(root, root / "savedata", {}, root / "cache");
  rex::RuntimeConfig config{};
  config.graphics = std::move(graphics);
  config.tool_mode = false;

  const auto status = runtime.Setup(std::move(config));
  if (status != rex::X_STATUS_SUCCESS) {
    runtime.Shutdown();
    return 20;
  }

  // No game image is loaded in this milestone. Cleanly exercise the runtime
  // teardown path after plugin and graphics-system initialization.
  runtime.Shutdown();
  return 0;
}
