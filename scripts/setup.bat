@echo off
REM NewsDigest Setup Script
REM Sets up the development environment on Windows

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "VENV_DIR=%PROJECT_ROOT%\.venv"

echo ========================================
echo NewsDigest Development Setup
echo ========================================
echo.

REM Check Python version
echo [1/6] Checking Python version...
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

if %PYTHON_MAJOR% LSS 3 (
    echo Error: Python 3.11+ is required ^(found %PYTHON_VERSION%^)
    exit /b 1
)
if %PYTHON_MAJOR% EQU 3 if %PYTHON_MINOR% LSS 11 (
    echo Error: Python 3.11+ is required ^(found %PYTHON_VERSION%^)
    exit /b 1
)
echo   Found Python %PYTHON_VERSION%

REM Create virtual environment
echo.
echo [2/6] Creating virtual environment...
if exist "%VENV_DIR%" (
    echo   Virtual environment already exists at %VENV_DIR%
) else (
    python -m venv "%VENV_DIR%"
    echo   Created virtual environment at %VENV_DIR%
)

REM Activate virtual environment
echo.
echo [3/6] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
echo   Activated

REM Upgrade pip
echo.
echo [4/6] Upgrading pip...
pip install --upgrade pip --quiet

REM Install dependencies
echo.
echo [5/6] Installing dependencies...
pip install -r "%PROJECT_ROOT%\requirements.txt" --quiet
pip install -r "%PROJECT_ROOT%\requirements-dev.txt" --quiet
pip install -e "%PROJECT_ROOT%" --quiet
echo   Dependencies installed

REM Download spaCy model
echo.
echo [6/6] Downloading spaCy language model...
python -m spacy download en_core_web_sm
echo   Model downloaded

REM Install pre-commit hooks
echo.
echo Installing pre-commit hooks...
where pre-commit >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    pre-commit install --quiet
    echo   Pre-commit hooks installed
) else (
    echo   Skipping pre-commit ^(not installed^)
)

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo To activate the virtual environment:
echo   .venv\Scripts\activate
echo.
echo To run tests:
echo   scripts\test.bat
echo.
echo To build:
echo   scripts\build.bat
echo.

endlocal
