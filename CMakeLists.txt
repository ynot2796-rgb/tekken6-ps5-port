cmake_minimum_required(VERSION 3.25)
project(t6_ps5_port_scaffold LANGUAGES C CXX)

# Architecture scaffold only; this target is not the game.
# Configure with a verified PS5 toolchain before treating it as a console build.
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(t6_platform_contract INTERFACE)
target_include_directories(t6_platform_contract INTERFACE
    "${CMAKE_CURRENT_SOURCE_DIR}/include")

add_executable(t6_port_probe
    src/main.cpp
    src/platform_probe.cpp)
target_link_libraries(t6_port_probe PRIVATE t6_platform_contract)

# No guessed SDK paths, proprietary game files, or server endpoints are included.
