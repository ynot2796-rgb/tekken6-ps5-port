#include "t6_platform.h"

namespace t6::platform {

Capabilities probe_capabilities() noexcept {
    // Do not claim support until an actual adapter is implemented and tested.
    return {};
}

const char* platform_name() noexcept {
#if defined(__ORBIS__)
    return "PS5 (adapter unimplemented)";
#elif defined(_WIN32)
    return "Windows host";
#elif defined(__linux__)
    return "Linux host";
#else
    return "unknown host";
#endif
}

} // namespace t6::platform
