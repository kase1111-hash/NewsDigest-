#!/usr/bin/env bash
# NewsDigest Build Script
# Builds distribution packages

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "NewsDigest Build"
echo "========================================"
echo ""

cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Clean previous builds
echo "[1/4] Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/ src/*.egg-info/
echo "  Cleaned"

# Run checks
echo ""
echo "[2/4] Running linter..."
ruff check src/ tests/ || { echo "Linting failed!"; exit 1; }
echo "  Linting passed"

echo ""
echo "[3/4] Running type checker..."
mypy src/ || echo "  Type check completed with warnings"

# Build packages
echo ""
echo "[4/4] Building distribution packages..."
python -m build
echo "  Build complete"

echo ""
echo "========================================"
echo "Build successful!"
echo "========================================"
echo ""
echo "Distribution packages created in dist/"
ls -la dist/
echo ""
