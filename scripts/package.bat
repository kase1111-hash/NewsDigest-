@echo off
REM NewsDigest Package Script
REM Builds distributable packages (wheel, sdist)

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

set BUILD_WHEEL=true
set BUILD_SDIST=true
set BUILD_DOCKER=false
set DOCKER_TAG=newsdigest:latest

:parse_args
if "%~1"=="" goto :main
if "%~1"=="--wheel-only" (
    set BUILD_SDIST=false
    set BUILD_DOCKER=false
    shift
    goto :parse_args
)
if "%~1"=="--sdist-only" (
    set BUILD_WHEEL=false
    set BUILD_DOCKER=false
    shift
    goto :parse_args
)
if "%~1"=="--docker" (
    set BUILD_DOCKER=true
    shift
    goto :parse_args
)
if "%~1"=="--docker-only" (
    set BUILD_WHEEL=false
    set BUILD_SDIST=false
    set BUILD_DOCKER=true
    shift
    goto :parse_args
)
if "%~1"=="--docker-tag" (
    set DOCKER_TAG=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--all" (
    set BUILD_WHEEL=true
    set BUILD_SDIST=true
    set BUILD_DOCKER=true
    shift
    goto :parse_args
)
if "%~1"=="-h" goto :show_help
if "%~1"=="--help" goto :show_help
echo Unknown option: %~1
exit /b 1

:show_help
echo Usage: %0 [OPTIONS]
echo.
echo Options:
echo   --wheel-only     Build only wheel package
echo   --sdist-only     Build only source distribution
echo   --docker         Also build Docker image
echo   --docker-only    Build only Docker image
echo   --docker-tag TAG Docker image tag (default: newsdigest:latest)
echo   --all            Build wheel, sdist, and Docker
echo   -h, --help       Show this help message
exit /b 0

:main
echo ========================================
echo NewsDigest Package Builder
echo ========================================
echo.

cd /d "%PROJECT_ROOT%"

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
for /d %%d in (src\*.egg-info) do rmdir /s /q "%%d"

REM Build Python packages
if "%BUILD_WHEEL%"=="true" (
    goto :build_python
)
if "%BUILD_SDIST%"=="true" (
    goto :build_python
)
goto :check_docker

:build_python
echo.
echo Installing build dependencies...
pip install --quiet build twine

set BUILD_ARGS=
if "%BUILD_WHEEL%"=="true" if "%BUILD_SDIST%"=="false" (
    set BUILD_ARGS=--wheel
)
if "%BUILD_WHEEL%"=="false" if "%BUILD_SDIST%"=="true" (
    set BUILD_ARGS=--sdist
)

echo.
echo Building Python packages...
python -m build %BUILD_ARGS%

echo.
echo Validating packages...
twine check dist\*

echo.
echo Python packages built successfully:
dir /b dist\

:check_docker
if "%BUILD_DOCKER%"=="false" goto :done

echo.
echo Building Docker image: %DOCKER_TAG%
docker build -f docker\Dockerfile -t %DOCKER_TAG% --target runtime .

echo.
echo Building Docker API image...
docker build -f docker\Dockerfile -t %DOCKER_TAG%-api --target api .

echo.
echo Docker images built successfully:
docker images | findstr newsdigest

:done
echo.
echo ========================================
echo Packaging complete!
echo ========================================

if "%BUILD_WHEEL%"=="true" (
    echo.
    echo Python packages are in: dist\
    echo.
    echo To install locally:
    echo   pip install dist\newsdigest-*.whl
    echo.
    echo To upload to PyPI:
    echo   twine upload dist\*
)

if "%BUILD_DOCKER%"=="true" (
    echo.
    echo Docker images:
    echo   %DOCKER_TAG% ^(CLI^)
    echo   %DOCKER_TAG%-api ^(API^)
)

endlocal
