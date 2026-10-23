#include "t6_platform.h"
#include <cstdio>

int main() {
    const auto caps = t6::platform::probe_capabilities();
    std::puts("Tekken 6 Native Online — PS5 port probe");
    std::printf("Platform adapter: %s\n", t6::platform::platform_name());
    std::printf("Controller: %s\n", caps.controller ? "yes" : "not implemented");
    std::printf("Audio: %s\n", caps.audio ? "yes" : "not implemented");
    std::printf("Networking: %s\n", caps.networking ? "yes" : "not implemented");
    std::printf("High-resolution timer: %s\n", caps.high_resolution_timer ? "yes" : "not implemented");
    std::printf("Graphics backend: %s\n", caps.graphics_backend ? "yes" : "not implemented");
    std::puts("Probe only: not the game and not yet tested on PS5.");
    return 0;
}
