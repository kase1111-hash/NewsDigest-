@echo off
REM NewsDigest Packaging Script for Windows
REM Builds distributable packages: wheel, sdist, zip, and standalone executable

setlocal EnableDelayedExpansion

REM Configuration
set "PROJECT_ROOT=%~dp0.."
set "DIST_DIR=%PROJECT_ROOT%\dist"
set "BUILD_DIR=%PROJECT_ROOT%\build"

REM Get version from pyproject.toml
for /f "tokens=*" %%i in ('python -c "import tomllib; print(tomllib.load(open('%PROJECT_ROOT:\=/%/pyproject.toml', 'rb'))['project']['version'])" 2^>nul') do set "VERSION=%%i"
if "%VERSION%"=="" set "VERSION=0.1.0"

echo.
echo ========================================
echo NewsDigest Packaging Script v%VERSION%
echo ========================================
echo.

REM Parse arguments
set "BUILD_WHEEL=0"
set "BUILD_SDIST=0"
set "BUILD_ZIP=0"
set "BUILD_EXE=0"
set "CLEAN=0"

if "%~1"=="" goto :usage

:parse_args
if "%~1"=="" goto :start_build
if /i "%~1"=="--wheel" set "BUILD_WHEEL=1" & shift & goto :parse_args
if /i "%~1"=="--sdist" set "BUILD_SDIST=1" & shift & goto :parse_args
if /i "%~1"=="--zip" set "BUILD_ZIP=1" & shift & goto :parse_args
if /i "%~1"=="--exe" set "BUILD_EXE=1" & shift & goto :parse_args
if /i "%~1"=="--all" (
    set "BUILD_WHEEL=1"
    set "BUILD_SDIST=1"
    set "BUILD_ZIP=1"
    set "BUILD_EXE=1"
    shift
    goto :parse_args
)
if /i "%~1"=="--clean" set "CLEAN=1" & shift & goto :parse_args
if /i "%~1"=="--help" goto :usage
if /i "%~1"=="-h" goto :usage
echo Unknown option: %~1
goto :usage

:usage
echo Usage: %~nx0 [OPTIONS]
echo.
echo Options:
echo   --wheel     Build Python wheel package (.whl)
echo   --sdist     Build source distribution (.tar.gz)
echo   --zip       Build zip archive
echo   --exe       Build standalone executable (requires PyInstaller)
echo   --all       Build all package types
echo   --clean     Clean build artifacts before building
echo   --help      Show this help message
echo.
echo Examples:
echo   %~nx0 --wheel --sdist    Build wheel and source distribution
echo   %~nx0 --all              Build all package types
echo   %~nx0 --clean --all      Clean and rebuild everything
exit /b 0

:start_build
cd /d "%PROJECT_ROOT%"

REM Clean if requested
if "%CLEAN%"=="1" (
    echo Cleaning build artifacts...
    if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
    if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
    if exist "src\*.egg-info" rmdir /s /q "src\*.egg-info"
    echo Cleaned!
    echo.
)

REM Create dist directory
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

REM Build wheel
if "%BUILD_WHEEL%"=="1" (
    echo Building wheel package...
    python -m pip install --quiet build wheel
    python -m build --wheel --outdir "%DIST_DIR%"
    if errorlevel 1 (
        echo ERROR: Wheel build failed!
        exit /b 1
    )
    echo Wheel built successfully!
    echo.
)

REM Build source distribution
if "%BUILD_SDIST%"=="1" (
    echo Building source distribution...
    python -m pip install --quiet build
    python -m build --sdist --outdir "%DIST_DIR%"
    if errorlevel 1 (
        echo ERROR: Source distribution build failed!
        exit /b 1
    )
    echo Source distribution built successfully!
    echo.
)

REM Build zip archive
if "%BUILD_ZIP%"=="1" (
    echo Building zip archive...

    set "ZIP_NAME=newsdigest-%VERSION%.zip"
    set "ZIP_PATH=%DIST_DIR%\!ZIP_NAME!"
    set "TEMP_DIR=%TEMP%\newsdigest-build-%RANDOM%"
    set "ZIP_CONTENT_DIR=!TEMP_DIR!\newsdigest-%VERSION%"

    mkdir "!ZIP_CONTENT_DIR!"

    REM Copy relevant files
    xcopy /s /e /i "src" "!ZIP_CONTENT_DIR!\src" >nul
    xcopy /s /e /i "config" "!ZIP_CONTENT_DIR!\config" >nul
    xcopy /s /e /i "scripts" "!ZIP_CONTENT_DIR!\scripts" >nul
    copy "pyproject.toml" "!ZIP_CONTENT_DIR!\" >nul
    copy "requirements.txt" "!ZIP_CONTENT_DIR!\" >nul
    copy "requirements-dev.txt" "!ZIP_CONTENT_DIR!\" >nul
    copy "requirements-all.txt" "!ZIP_CONTENT_DIR!\" >nul
    copy "README.md" "!ZIP_CONTENT_DIR!\" >nul
    copy "Makefile" "!ZIP_CONTENT_DIR!\" >nul
    copy ".env.example" "!ZIP_CONTENT_DIR!\" >nul

    REM Copy docker files if they exist
    if exist "docker" xcopy /s /e /i "docker" "!ZIP_CONTENT_DIR!\docker" >nul

    REM Create zip using PowerShell
    powershell -Command "Compress-Archive -Path '!ZIP_CONTENT_DIR!' -DestinationPath '!ZIP_PATH!' -Force"

    REM Cleanup
    rmdir /s /q "!TEMP_DIR!"

    echo Zip archive built: !ZIP_PATH!
    echo.
)

REM Build standalone executable
if "%BUILD_EXE%"=="1" (
    echo Building standalone executable...

    REM Check for PyInstaller
    python -c "import PyInstaller" 2>nul
    if errorlevel 1 (
        echo Installing PyInstaller...
        python -m pip install --quiet pyinstaller
    )

    REM Check for spec file
    set "SPEC_FILE=%PROJECT_ROOT%\newsdigest.spec"
    if exist "!SPEC_FILE!" (
        echo Using spec file: !SPEC_FILE!
        python -m PyInstaller "!SPEC_FILE!" --distpath "%DIST_DIR%" --workpath "%BUILD_DIR%\pyinstaller"
    ) else (
        echo Building with default PyInstaller options...
        python -m PyInstaller ^
            --name newsdigest ^
            --onefile ^
            --console ^
            --distpath "%DIST_DIR%" ^
            --workpath "%BUILD_DIR%\pyinstaller" ^
            --specpath "%BUILD_DIR%" ^
            --add-data "src\newsdigest;newsdigest" ^
            --hidden-import=click ^
            --hidden-import=rich ^
            --hidden-import=httpx ^
            --hidden-import=bs4 ^
            --hidden-import=lxml ^
            --hidden-import=feedparser ^
            --hidden-import=pydantic ^
            --hidden-import=yaml ^
            --hidden-import=dotenv ^
            src\newsdigest\cli\main.py
    )

    if errorlevel 1 (
        echo ERROR: Executable build failed!
        exit /b 1
    )

    REM Rename with version
    if exist "%DIST_DIR%\newsdigest.exe" (
        move "%DIST_DIR%\newsdigest.exe" "%DIST_DIR%\newsdigest-%VERSION%-windows.exe" >nul
    )

    echo Standalone executable built successfully!
    echo.
)

REM Summary
echo.
echo ========================================
echo Build complete! Packages in: %DIST_DIR%
echo ========================================
echo.
dir "%DIST_DIR%"

endlocal
exit /b 0
