/*
 * POSIX Poll implementation for the pinned Native Online GGPO fork.
 * UDP in this fork is pumped through OnLoopPoll; registered handles are
 * additionally supported as file descriptors for future integration.
 */
#include "types.h"
#include "poll.h"
#include <cerrno>
#include <poll.h>
#include <vector>

Poll::Poll() : _handle_count(0), _start_time(0) {}

void Poll::RegisterHandle(IPollSink *sink, HANDLE h, void *cookie) {
    ASSERT(_handle_count < MAX_POLLABLE_HANDLES);
    _handles[_handle_count] = h;
    _handle_sinks[_handle_count] = PollSinkCb(sink, cookie);
    ++_handle_count;
}

void Poll::RegisterMsgLoop(IPollSink *sink, void *cookie) {
    _msg_sinks.push_back(PollSinkCb(sink, cookie));
}
void Poll::RegisterLoop(IPollSink *sink, void *cookie) {
    _loop_sinks.push_back(PollSinkCb(sink, cookie));
}
void Poll::RegisterPeriodic(IPollSink *sink, int interval, void *cookie) {
    _periodic_sinks.push_back(PollPeriodicSinkCb(sink, cookie, interval));
}
void Poll::Run() {
    while (Pump(100)) {}
}
bool Poll::Pump(int timeout) {
    if (_start_time == 0) _start_time = static_cast<int>(Platform::GetCurrentTimeMS());
    const int elapsed = static_cast<int>(Platform::GetCurrentTimeMS()) - _start_time;
    const int maxwait = ComputeWaitTime(elapsed);
    if (maxwait != INFINITE) timeout = MIN(timeout, maxwait);

    std::vector<struct pollfd> fds;
    fds.reserve(_handle_count);
    for (int i = 0; i < _handle_count; ++i) {
        struct pollfd fd{};
        fd.fd = _handles[i];
        fd.events = POLLIN;
        fds.push_back(fd);
    }
    const int ready = ::poll(fds.empty() ? nullptr : fds.data(),
                             static_cast<nfds_t>(fds.size()), timeout);
    bool finished = false;
    if (ready > 0) {
        for (int i = 0; i < _handle_count; ++i) {
            if (fds[i].revents & (POLLIN | POLLERR | POLLHUP | POLLNVAL)) {
                finished = !(_handle_sinks[i].sink->OnHandlePoll(_handle_sinks[i].cookie)) || finished;
            }
        }
    } else if (ready < 0 && errno != EINTR) {
        Log("poll() failed: %d\n", errno);
    }
    for (int i = 0; i < _msg_sinks.size(); ++i) {
        PollSinkCb &cb = _msg_sinks[i];
        finished = !cb.sink->OnMsgPoll(cb.cookie) || finished;
    }
    for (int i = 0; i < _periodic_sinks.size(); ++i) {
        PollPeriodicSinkCb &cb = _periodic_sinks[i];
        if (cb.interval > 0 && cb.interval + cb.last_fired <= elapsed) {
            cb.last_fired = (elapsed / cb.interval) * cb.interval;
            finished = !cb.sink->OnPeriodicPoll(cb.cookie, cb.last_fired) || finished;
        }
    }
    for (int i = 0; i < _loop_sinks.size(); ++i) {
        PollSinkCb &cb = _loop_sinks[i];
        finished = !cb.sink->OnLoopPoll(cb.cookie) || finished;
    }
    return finished;
}
int Poll::ComputeWaitTime(int elapsed) {
    int waitTime = INFINITE;
    for (int i = 0; i < _periodic_sinks.size(); ++i) {
        PollPeriodicSinkCb &cb = _periodic_sinks[i];
        if (cb.interval <= 0) continue;
        const int timeout = (cb.interval + cb.last_fired) - elapsed;
        if (waitTime == INFINITE || timeout < waitTime) waitTime = MAX(timeout, 0);
    }
    return waitTime;
}
