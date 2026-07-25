cmake_minimum_required(VERSION 3.16)
project(InnerMonologueEngine VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Main executable
add_executable(ime
    src/main.cpp
    src/resonance_gate.cpp
    src/journal_reader.cpp
)

target_include_directories(ime PRIVATE src)

# Tests
enable_testing()
add_executable(test_ime tests/test_resonance_gate.cpp src/resonance_gate.cpp)
target_include_directories(test_ime PRIVATE src)
add_test(NAME ResonanceGateTests COMMAND test_ime)
