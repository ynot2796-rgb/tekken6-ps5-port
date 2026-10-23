#pragma once
/*
 * POSIX platform shim for the pinned Tekken 6 Native Online GGPO fork.
 * Intended for Linux CI and the FreeBSD-derived PS5 userland; it does not
 * emulate the Windows launcher or the game's DirectX renderer.
 */
#include "t6_socket_compat.h"
#include <cstdio>
#include <cerrno>
#include <cstdlib>
#include <cstring>
#include <strings.h>
#include <sys/types.h>
#include <unistd.h>
#include <time.h>

using DWORD = unsigned long;
using HANDLE = int;
#ifndef INFINITE
#  define INFINITE 0x7fffffff
#endif

class Platform {
public:
    using ProcessID = pid_t;
    static ProcessID GetProcessID() { return ::getpid(); }
    static void AssertFailed(char *msg) {
        ::fprintf(stderr, "%s\n", msg ? msg : "GGPO assertion failed");
        ::fflush(stderr);
    }
    static uint32 GetCurrentTimeMS() {
        struct timespec ts{};
        if (::clock_gettime(CLOCK_MONOTONIC, &ts) != 0) return 0;
        return static_cast<uint32>(ts.tv_sec * 1000u + ts.tv_nsec / 1000000u);
    }
    static int GetConfigInt(const char *name);
    static bool GetConfigBool(const char *name);
};

/* The fork uses MSVC secure-CRT helpers. Keep equivalent bounded POSIX calls. */
#ifndef _MSC_VER
#  define sprintf_s(buffer, size, ...) std::snprintf((buffer), (size), __VA_ARGS__)
#  define vsprintf_s(buffer, size, fmt, args) std::vsnprintf((buffer), (size), (fmt), (args))
#  define strcpy_s(dst, src) std::snprintf((dst), sizeof(dst), "%s", (src))
#  define fopen_s(out, path, mode) ((*(out) = std::fopen((path), (mode))) == nullptr ? errno : 0)
#endif
#ifndef FALSE
#  define FALSE 0
#endif
#ifndef TRUE
#  define TRUE 1
#endif
