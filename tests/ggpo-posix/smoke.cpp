#include "types.h"
#include "poll.h"

#include <cstdio>

class SmokeSink final : public IPollSink {
public:
    int calls = 0;
    bool OnLoopPoll(void *) override {
        ++calls;
        return true;
    }
};

int main() {
    const uint32 before = Platform::GetCurrentTimeMS();
    const uint32 after = Platform::GetCurrentTimeMS();
    if (after < before) {
        std::fprintf(stderr, "monotonic platform clock moved backwards\n");
        return 1;
    }

    Poll poller;
    SmokeSink sink;
    poller.RegisterLoop(&sink);
    if (poller.Pump(0)) {
        std::fprintf(stderr, "poller unexpectedly requested shutdown\n");
        return 2;
    }
    if (sink.calls != 1) {
        std::fprintf(stderr, "loop callback count was %d, expected 1\n", sink.calls);
        return 3;
    }
    std::puts("GGPO POSIX platform clock and poll callback passed");
    return 0;
}
