# cpp_core/CMakeLists.txt (ZWEITE KORRIGIERTE VERSION)

cmake_minimum_required(VERSION 3.15)
project(capa_core)

# --- pybind11 als Submodul einbinden ---
add_subdirectory(vendor/pybind11)

# --- Python Module Definition ---
# HIER IST DIE KORREKTUR: Wir verwenden eine Variable, um die Pfade explizit zu machen.
pybind11_add_module(capa_core
    "${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/short_term_memory.cpp"
)

# --- Include-Pfade für Abhängigkeiten setzen ---
target_include_directories(capa_core PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/src"
    "${CMAKE_CURRENT_SOURCE_DIR}/vendor/msgpack-c/include"
)

# Set C++ standard to 17 for modern features
set_target_properties(capa_core PROPERTIES CXX_STANDARD 17)