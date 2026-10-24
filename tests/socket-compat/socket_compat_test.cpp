#include "t6_socket_compat.h"

#include <array>
#include <cstdio>
#include <cstring>

int main() {
    const SOCKET receiver = ::socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (receiver == INVALID_SOCKET) return 1;

    sockaddr_in local{};
    local.sin_family = AF_INET;
    local.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    local.sin_port = 0;
    if (::bind(receiver, reinterpret_cast<sockaddr*>(&local), sizeof(local)) == SOCKET_ERROR) {
        closesocket(receiver);
        return 2;
    }

    socklen_t local_size = sizeof(local);
    if (::getsockname(receiver, reinterpret_cast<sockaddr*>(&local), &local_size) == SOCKET_ERROR) {
        closesocket(receiver);
        return 3;
    }

    const SOCKET sender = ::socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sender == INVALID_SOCKET) {
        closesocket(receiver);
        return 4;
    }

    constexpr char payload[] = "t6-ggpo-udp-compat";
    if (::sendto(sender, payload, sizeof(payload), 0,
                 reinterpret_cast<sockaddr*>(&local), sizeof(local)) != sizeof(payload)) {
        closesocket(sender);
        closesocket(receiver);
        return 5;
    }

    std::array<char, 64> received{};
    const auto count = ::recvfrom(receiver, received.data(), received.size(), 0, nullptr, nullptr);
    closesocket(sender);
    closesocket(receiver);
    if (count != sizeof(payload) || std::memcmp(received.data(), payload, sizeof(payload)) != 0) {
        return 6;
    }
    std::puts("POSIX UDP socket compatibility: PASS");
    return 0;
}
