@echo off
REM NewsDigest Check Script
REM Runs all quality checks (lint, type-check, security-scan)

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

echo ========================================
echo NewsDigest Quality Checks
echo ========================================
echo.

cd /d "%PROJECT_ROOT%"

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

set FAILED=0

REM Lint
echo [1/4] Running linter ^(ruff^)...
ruff check src/ tests/
if %ERRORLEVEL% NEQ 0 (
    echo   FAILED
    set FAILED=1
) else (
    echo   PASSED
)
echo.

REM Format check
echo [2/4] Checking code formatting...
ruff format --check src/ tests/
if %ERRORLEVEL% NEQ 0 (
    echo   FAILED ^(run 'ruff format src/ tests/' to fix^)
    set FAILED=1
) else (
    echo   PASSED
)
echo.

REM Type check
echo [3/4] Running type checker ^(mypy^)...
mypy src/
echo   Type check completed
echo.

REM Security scan
echo [4/4] Running security scan ^(bandit^)...
where bandit >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    bandit -r src/ -c pyproject.toml -q
    echo   Security scan completed
) else (
    echo   SKIPPED ^(bandit not installed^)
)
echo.

echo ========================================
if %FAILED% EQU 0 (
    echo All checks passed!
) else (
    echo Some checks failed!
    exit /b 1
)
echo ========================================

endlocal
