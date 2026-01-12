@echo off
REM NewsDigest Test Script
REM Runs the test suite

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

set COVERAGE=false
set VERBOSE=false
set TEST_PATH=tests/

:parse_args
if "%~1"=="" goto :run_tests
if "%~1"=="-c" (
    set COVERAGE=true
    shift
    goto :parse_args
)
if "%~1"=="--coverage" (
    set COVERAGE=true
    shift
    goto :parse_args
)
if "%~1"=="-v" (
    set VERBOSE=true
    shift
    goto :parse_args
)
if "%~1"=="--verbose" (
    set VERBOSE=true
    shift
    goto :parse_args
)
if "%~1"=="-h" goto :show_help
if "%~1"=="--help" goto :show_help
set TEST_PATH=%~1
shift
goto :parse_args

:show_help
echo Usage: %0 [OPTIONS] [TEST_PATH]
echo.
echo Options:
echo   -c, --coverage    Run with coverage reporting
echo   -v, --verbose     Verbose output
echo   -h, --help        Show this help message
echo.
echo Examples:
echo   %0                      # Run all tests
echo   %0 -c                   # Run with coverage
echo   %0 tests\unit\          # Run unit tests only
echo   %0 -v tests\integration # Run integration tests verbosely
exit /b 0

:run_tests
echo ========================================
echo NewsDigest Test Suite
echo ========================================
echo.

cd /d "%PROJECT_ROOT%"

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Build pytest arguments
set PYTEST_ARGS=

if "%VERBOSE%"=="true" (
    set PYTEST_ARGS=%PYTEST_ARGS% -v
)

if "%COVERAGE%"=="true" (
    set PYTEST_ARGS=%PYTEST_ARGS% --cov=src/newsdigest --cov-report=html --cov-report=term
)

set PYTEST_ARGS=%PYTEST_ARGS% %TEST_PATH%

REM Run tests
echo Running: pytest %PYTEST_ARGS%
echo.

pytest %PYTEST_ARGS%

echo.
echo ========================================
echo Tests complete!
echo ========================================

if "%COVERAGE%"=="true" (
    echo.
    echo Coverage report generated in htmlcov/
)

endlocal
