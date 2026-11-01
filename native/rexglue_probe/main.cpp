#include <filesystem>
#include <memory>

#include <rex/runtime.h>
#include <rex/system/gpu_plugin.h>

// Native runtime/plugin link smoke only. It deliberately uses empty data paths:
// no writable title-directory assumptions, generated PPC mappings, XEX or game
// assets are required for this initialization/teardown check.
int main() {
  auto graphics = rex::system::LoadGpuPlugin("xenos", "vulkan");
  if (!graphics) {
    return 10;
  }

  rex::Runtime runtime(std::filesystem::path{});
  rex::RuntimeConfig config{};
  config.graphics = std::move(graphics);
  config.tool_mode = false;

  const auto status = runtime.Setup(std::move(config));
  if (status != X_STATUS_SUCCESS) {
    runtime.Shutdown();
    return 20;
  }

  // No game image is loaded in this milestone. Cleanly exercise runtime,
  // memory-system and Vulkan/Xenos backend initialization and teardown.
  runtime.Shutdown();
  return 0;
}
