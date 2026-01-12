#!/bin/bash
# NewsDigest Packaging Script
# Builds distributable packages: wheel, sdist, zip, and standalone executable

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${PROJECT_ROOT}/dist"
BUILD_DIR="${PROJECT_ROOT}/build"
VERSION=$(python3 -c "import tomllib; print(tomllib.load(open('${PROJECT_ROOT}/pyproject.toml', 'rb'))['project']['version'])" 2>/dev/null || echo "0.1.0")

echo -e "${BLUE}NewsDigest Packaging Script v${VERSION}${NC}"
echo "================================================"

# Parse arguments
BUILD_WHEEL=false
BUILD_SDIST=false
BUILD_ZIP=false
BUILD_EXE=false
BUILD_ALL=false
CLEAN=false

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --wheel     Build Python wheel package (.whl)"
    echo "  --sdist     Build source distribution (.tar.gz)"
    echo "  --zip       Build zip archive"
    echo "  --exe       Build standalone executable (requires PyInstaller)"
    echo "  --all       Build all package types"
    echo "  --clean     Clean build artifacts before building"
    echo "  --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --wheel --sdist    # Build wheel and source distribution"
    echo "  $0 --all              # Build all package types"
    echo "  $0 --clean --all      # Clean and rebuild everything"
    exit 0
}

if [ $# -eq 0 ]; then
    usage
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --wheel)
            BUILD_WHEEL=true
            shift
            ;;
        --sdist)
            BUILD_SDIST=true
            shift
            ;;
        --zip)
            BUILD_ZIP=true
            shift
            ;;
        --exe)
            BUILD_EXE=true
            shift
            ;;
        --all)
            BUILD_ALL=true
            shift
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

if [ "$BUILD_ALL" = true ]; then
    BUILD_WHEEL=true
    BUILD_SDIST=true
    BUILD_ZIP=true
    BUILD_EXE=true
fi

cd "$PROJECT_ROOT"

# Clean if requested
if [ "$CLEAN" = true ]; then
    echo -e "${YELLOW}Cleaning build artifacts...${NC}"
    rm -rf "$DIST_DIR" "$BUILD_DIR" src/*.egg-info *.egg-info
    echo -e "${GREEN}Cleaned!${NC}"
fi

# Create dist directory
mkdir -p "$DIST_DIR"

# Build wheel
if [ "$BUILD_WHEEL" = true ]; then
    echo -e "${BLUE}Building wheel package...${NC}"
    python3 -m pip install --quiet build wheel
    python3 -m build --wheel --outdir "$DIST_DIR"
    echo -e "${GREEN}Wheel built: ${DIST_DIR}/newsdigest-${VERSION}-py3-none-any.whl${NC}"
fi

# Build source distribution
if [ "$BUILD_SDIST" = true ]; then
    echo -e "${BLUE}Building source distribution...${NC}"
    python3 -m pip install --quiet build
    python3 -m build --sdist --outdir "$DIST_DIR"
    echo -e "${GREEN}Source distribution built: ${DIST_DIR}/newsdigest-${VERSION}.tar.gz${NC}"
fi

# Build zip archive
if [ "$BUILD_ZIP" = true ]; then
    echo -e "${BLUE}Building zip archive...${NC}"
    ZIP_NAME="newsdigest-${VERSION}.zip"
    ZIP_PATH="${DIST_DIR}/${ZIP_NAME}"

    # Create temporary directory for zip contents
    TEMP_DIR=$(mktemp -d)
    ZIP_CONTENT_DIR="${TEMP_DIR}/newsdigest-${VERSION}"
    mkdir -p "$ZIP_CONTENT_DIR"

    # Copy relevant files
    cp -r src "$ZIP_CONTENT_DIR/"
    cp -r config "$ZIP_CONTENT_DIR/"
    cp -r scripts "$ZIP_CONTENT_DIR/"
    cp pyproject.toml "$ZIP_CONTENT_DIR/"
    cp requirements.txt "$ZIP_CONTENT_DIR/"
    cp requirements-dev.txt "$ZIP_CONTENT_DIR/"
    cp requirements-all.txt "$ZIP_CONTENT_DIR/"
    cp README.md "$ZIP_CONTENT_DIR/"
    cp Makefile "$ZIP_CONTENT_DIR/"
    cp .env.example "$ZIP_CONTENT_DIR/"

    # Copy docker files if they exist
    if [ -d "docker" ]; then
        cp -r docker "$ZIP_CONTENT_DIR/"
    fi

    # Create zip
    (cd "$TEMP_DIR" && zip -r "$ZIP_PATH" "newsdigest-${VERSION}")

    # Cleanup
    rm -rf "$TEMP_DIR"

    echo -e "${GREEN}Zip archive built: ${ZIP_PATH}${NC}"
fi

# Build standalone executable
if [ "$BUILD_EXE" = true ]; then
    echo -e "${BLUE}Building standalone executable...${NC}"

    # Check for PyInstaller
    if ! python3 -c "import PyInstaller" 2>/dev/null; then
        echo -e "${YELLOW}Installing PyInstaller...${NC}"
        python3 -m pip install --quiet pyinstaller
    fi

    # Check for spec file
    SPEC_FILE="${PROJECT_ROOT}/newsdigest.spec"
    if [ -f "$SPEC_FILE" ]; then
        echo "Using spec file: $SPEC_FILE"
        python3 -m PyInstaller "$SPEC_FILE" --distpath "$DIST_DIR" --workpath "$BUILD_DIR/pyinstaller"
    else
        echo "Building with default PyInstaller options..."
        python3 -m PyInstaller \
            --name newsdigest \
            --onefile \
            --console \
            --distpath "$DIST_DIR" \
            --workpath "$BUILD_DIR/pyinstaller" \
            --specpath "$BUILD_DIR" \
            --add-data "src/newsdigest:newsdigest" \
            --hidden-import=click \
            --hidden-import=rich \
            --hidden-import=httpx \
            --hidden-import=bs4 \
            --hidden-import=lxml \
            --hidden-import=feedparser \
            --hidden-import=pydantic \
            --hidden-import=yaml \
            --hidden-import=dotenv \
            src/newsdigest/cli/main.py
    fi

    # Detect platform for executable name
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        EXE_NAME="newsdigest-${VERSION}-linux"
        [ -f "${DIST_DIR}/newsdigest" ] && mv "${DIST_DIR}/newsdigest" "${DIST_DIR}/${EXE_NAME}"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        EXE_NAME="newsdigest-${VERSION}-macos"
        [ -f "${DIST_DIR}/newsdigest" ] && mv "${DIST_DIR}/newsdigest" "${DIST_DIR}/${EXE_NAME}"
    fi

    echo -e "${GREEN}Standalone executable built: ${DIST_DIR}/${EXE_NAME:-newsdigest}${NC}"
fi

# Summary
echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}Build complete! Packages in: ${DIST_DIR}${NC}"
echo ""
ls -la "$DIST_DIR"
