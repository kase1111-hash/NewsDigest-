@echo off
REM NewsDigest Build Script
REM Builds distribution packages

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

echo ========================================
echo NewsDigest Build
echo ========================================
echo.

cd /d "%PROJECT_ROOT%"

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Clean previous builds
echo [1/4] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
for /d %%d in (*.egg-info) do rmdir /s /q "%%d"
for /d %%d in (src\*.egg-info) do rmdir /s /q "%%d"
echo   Cleaned

REM Run checks
echo.
echo [2/4] Running linter...
ruff check src/ tests/
if %ERRORLEVEL% NEQ 0 (
    echo Linting failed!
    exit /b 1
)
echo   Linting passed

echo.
echo [3/4] Running type checker...
mypy src/
echo   Type check completed

REM Build packages
echo.
echo [4/4] Building distribution packages...
python -m build
echo   Build complete

echo.
echo ========================================
echo Build successful!
echo ========================================
echo.
echo Distribution packages created in dist/
dir dist\
echo.

endlocal
