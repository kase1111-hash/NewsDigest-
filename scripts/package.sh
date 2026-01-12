#!/usr/bin/env bash
# NewsDigest Package Script
# Builds distributable packages (wheel, sdist, Docker)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Package types to build
BUILD_WHEEL=true
BUILD_SDIST=true
BUILD_DOCKER=false
DOCKER_TAG="newsdigest:latest"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --wheel-only)
            BUILD_SDIST=false
            BUILD_DOCKER=false
            shift
            ;;
        --sdist-only)
            BUILD_WHEEL=false
            BUILD_DOCKER=false
            shift
            ;;
        --docker)
            BUILD_DOCKER=true
            shift
            ;;
        --docker-only)
            BUILD_WHEEL=false
            BUILD_SDIST=false
            BUILD_DOCKER=true
            shift
            ;;
        --docker-tag)
            DOCKER_TAG="$2"
            shift 2
            ;;
        --all)
            BUILD_WHEEL=true
            BUILD_SDIST=true
            BUILD_DOCKER=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --wheel-only     Build only wheel package"
            echo "  --sdist-only     Build only source distribution"
            echo "  --docker         Also build Docker image"
            echo "  --docker-only    Build only Docker image"
            echo "  --docker-tag TAG Docker image tag (default: newsdigest:latest)"
            echo "  --all            Build wheel, sdist, and Docker"
            echo "  -h, --help       Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}========================================"
echo "NewsDigest Package Builder"
echo -e "========================================${NC}"
echo ""

cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [[ -f ".venv/bin/activate" ]]; then
    source .venv/bin/activate
fi

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf build/ dist/ src/*.egg-info/

# Build Python packages
if [[ "$BUILD_WHEEL" == true ]] || [[ "$BUILD_SDIST" == true ]]; then
    echo ""
    echo -e "${BLUE}Installing build dependencies...${NC}"
    pip install --quiet build twine

    BUILD_ARGS=""
    if [[ "$BUILD_WHEEL" == true ]] && [[ "$BUILD_SDIST" == false ]]; then
        BUILD_ARGS="--wheel"
    elif [[ "$BUILD_WHEEL" == false ]] && [[ "$BUILD_SDIST" == true ]]; then
        BUILD_ARGS="--sdist"
    fi

    echo ""
    echo -e "${BLUE}Building Python packages...${NC}"
    python -m build $BUILD_ARGS

    echo ""
    echo -e "${BLUE}Validating packages...${NC}"
    twine check dist/*

    echo ""
    echo -e "${GREEN}Python packages built successfully:${NC}"
    ls -lh dist/
fi

# Build Docker image
if [[ "$BUILD_DOCKER" == true ]]; then
    echo ""
    echo -e "${BLUE}Building Docker image: $DOCKER_TAG${NC}"

    docker build \
        -f docker/Dockerfile \
        -t "$DOCKER_TAG" \
        --target runtime \
        .

    # Also build API image
    API_TAG="${DOCKER_TAG%-*}-api:${DOCKER_TAG##*:}"
    if [[ "$DOCKER_TAG" == *":"* ]]; then
        API_TAG="${DOCKER_TAG%:*}-api:${DOCKER_TAG##*:}"
    else
        API_TAG="${DOCKER_TAG}-api"
    fi

    echo ""
    echo -e "${BLUE}Building Docker API image: $API_TAG${NC}"

    docker build \
        -f docker/Dockerfile \
        -t "$API_TAG" \
        --target api \
        .

    echo ""
    echo -e "${GREEN}Docker images built successfully:${NC}"
    docker images | grep newsdigest
fi

echo ""
echo -e "${GREEN}========================================"
echo "Packaging complete!"
echo -e "========================================${NC}"

if [[ "$BUILD_WHEEL" == true ]] || [[ "$BUILD_SDIST" == true ]]; then
    echo ""
    echo "Python packages are in: dist/"
    echo ""
    echo "To install locally:"
    echo "  pip install dist/newsdigest-*.whl"
    echo ""
    echo "To upload to PyPI:"
    echo "  twine upload dist/*"
fi

if [[ "$BUILD_DOCKER" == true ]]; then
    echo ""
    echo "Docker images:"
    echo "  $DOCKER_TAG (CLI)"
    echo "  $API_TAG (API)"
    echo ""
    echo "To run:"
    echo "  docker run --rm $DOCKER_TAG --help"
fi
