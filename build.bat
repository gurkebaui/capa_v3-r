@echo off
REM build.bat - Builds the C++ core module for Windows

echo "--- Configuring CMake ---"
cmake -S cpp_core -B build -G "Visual Studio 17 2022" -A x64

if %errorlevel% neq 0 (
    echo "CMake configuration failed."
    exit /b %errorlevel%
)

echo "--- Building with MSBuild ---"
cmake --build build --config Release

if %errorlevel% neq 0 (
    echo "Build failed."
    exit /b %errorlevel%
)

echo "--- Copying module to root folder ---"
copy "build\Release\capa_core.cp*.pyd" "capa_core.pyd"

if %errorlevel% neq 0 (
    echo "Failed to copy the compiled module."
    exit /b %errorlevel%
)

echo "--- Build successful! capa_core.pyd is ready. ---"