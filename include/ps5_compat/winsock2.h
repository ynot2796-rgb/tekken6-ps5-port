#pragma once
#include "t6_socket_compat.h"
#include <cstdint>
struct WSADATA { uint16_t version = 0x0202; uint16_t high_version = 0x0202; };
#ifndef MAKEWORD
#  define MAKEWORD(low, high) (static_cast<unsigned short>((static_cast<unsigned char>(low)) | (static_cast<unsigned short>(static_cast<unsigned char>(high)) << 8)))
#endif
inline int WSAStartup(unsigned short, WSADATA *data) {
    if (data) { data->version = 0x0202; data->high_version = 0x0202; }
    return 0;
}
inline int WSACleanup() { return 0; }
