# cpp_core/CMakeLists.txt

cmake_minimum_required(VERSION 3.15)
project(capa_core)

# --- Add Submodules ---
add_subdirectory(vendor/pybind11)
add_subdirectory(vendor/msgpack-c)

# --- Python Module Definition ---
# pybind11_add_module is a helper function from pybind11
# It creates a Python extension module.
pybind11_add_module(capa_core
    src/main.cpp
    src/short_term_memory.cpp
)

# --- Link Dependencies ---
target_include_directories(capa_core PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${msgpack-c_SOURCE_DIR}/include # Include path for msgpack
)

# Set C++ standard to 17 for modern features
set_target_properties(capa_core PROPERTIES CXX_STANDARD 17)