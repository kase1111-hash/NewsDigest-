#!/usr/bin/env bash
# NewsDigest Setup Script
# Sets up the development environment on Unix/Linux/macOS

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_ROOT/.venv"

echo "========================================"
echo "NewsDigest Development Setup"
echo "========================================"
echo ""

# Check Python version
echo "[1/6] Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]; }; then
    echo "Error: Python 3.11+ is required (found $PYTHON_VERSION)"
    exit 1
fi
echo "  Found Python $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "[2/6] Creating virtual environment..."
if [ -d "$VENV_DIR" ]; then
    echo "  Virtual environment already exists at $VENV_DIR"
else
    python3 -m venv "$VENV_DIR"
    echo "  Created virtual environment at $VENV_DIR"
fi

# Activate virtual environment
echo ""
echo "[3/6] Activating virtual environment..."
source "$VENV_DIR/bin/activate"
echo "  Activated"

# Upgrade pip
echo ""
echo "[4/6] Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "[5/6] Installing dependencies..."
pip install -r "$PROJECT_ROOT/requirements.txt" --quiet
pip install -r "$PROJECT_ROOT/requirements-dev.txt" --quiet
pip install -e "$PROJECT_ROOT" --quiet
echo "  Dependencies installed"

# Download spaCy model
echo ""
echo "[6/6] Downloading spaCy language model..."
python -m spacy download en_core_web_sm --quiet 2>/dev/null || python -m spacy download en_core_web_sm
echo "  Model downloaded"

# Install pre-commit hooks
echo ""
echo "Installing pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install --quiet
    echo "  Pre-commit hooks installed"
else
    echo "  Skipping pre-commit (not installed)"
fi

echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "To activate the virtual environment:"
echo "  source .venv/bin/activate"
echo ""
echo "To run tests:"
echo "  make test"
echo "  # or: ./scripts/test.sh"
echo ""
echo "To build:"
echo "  make build"
echo "  # or: ./scripts/build.sh"
echo ""
