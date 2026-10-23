#pragma once

/*
 * Minimal WinSock-shaped socket surface for the Native Online GGPO port.
 *
 * This is intentionally limited to the datagram/socket calls currently used
 * by third_party/ggpo. It does not emulate Win32 events, threads, timers, or
 * the game's launcher. Keep the Windows path byte-for-byte unchanged.
 */
#if defined(_WIN32)
#  include <winsock2.h>
#  include <ws2tcpip.h>
#else
#  include <cerrno>
#  include <cstdint>
#  include <fcntl.h>
#  include <sys/ioctl.h>
#  include <sys/socket.h>
#  include <sys/types.h>
#  include <unistd.h>
#  include <arpa/inet.h>
#  include <netinet/in.h>
#  include <netdb.h>

using SOCKET = int;
using u_long = unsigned long;

#ifndef INVALID_SOCKET
#  define INVALID_SOCKET (-1)
#endif
#ifndef SOCKET_ERROR
#  define SOCKET_ERROR (-1)
#endif
#ifndef WSAEWOULDBLOCK
#  define WSAEWOULDBLOCK EWOULDBLOCK
#endif
#ifndef SO_DONTLINGER
#  define SO_DONTLINGER 0x7fff
#endif

inline int WSAGetLastError() noexcept { return errno; }
inline int closesocket(SOCKET s) noexcept { return ::close(s); }
inline int ioctlsocket(SOCKET s, long request, u_long* value) noexcept {
    if (request != FIONBIO || value == nullptr) {
        errno = EINVAL;
        return SOCKET_ERROR;
    }
    const int flags = ::fcntl(s, F_GETFL, 0);
    if (flags < 0) return SOCKET_ERROR;
    return ::fcntl(s, F_SETFL, *value ? (flags | O_NONBLOCK) : (flags & ~O_NONBLOCK));
}

/* WinSock's SO_DONTLINGER has no POSIX equivalent; keep setsockopt harmless. */
inline int t6_setsockopt_compat(SOCKET s, int level, int option,
                                const char* value, socklen_t length) noexcept {
#  ifdef SO_DONTLINGER
    if (option == SO_DONTLINGER) {
        linger l{};
        l.l_onoff = 0;
        l.l_linger = 0;
        return ::setsockopt(s, SOL_SOCKET, SO_LINGER,
                            reinterpret_cast<const char*>(&l), sizeof(l));
    }
#  endif
    return ::setsockopt(s, level, option, value, length);
}
#  define setsockopt t6_setsockopt_compat
#endif
