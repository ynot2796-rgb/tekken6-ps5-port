#pragma once

namespace t6::platform {

// Platform probe only. Implement these via a verified target SDK/runtime.
struct Capabilities {
    bool controller = false;
    bool audio = false;
    bool networking = false;
    bool high_resolution_timer = false;
    bool graphics_backend = false;
};

Capabilities probe_capabilities() noexcept;
const char* platform_name() noexcept;

} // namespace t6::platform
