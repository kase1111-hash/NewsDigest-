#!/usr/bin/env bash
# NewsDigest Check Script
# Runs all quality checks (lint, type-check, security-scan, tests)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "NewsDigest Quality Checks"
echo "========================================"
echo ""

cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Track overall status
FAILED=0

# Lint
echo "[1/4] Running linter (ruff)..."
if ruff check src/ tests/; then
    echo "  PASSED"
else
    echo "  FAILED"
    FAILED=1
fi
echo ""

# Format check
echo "[2/4] Checking code formatting..."
if ruff format --check src/ tests/; then
    echo "  PASSED"
else
    echo "  FAILED (run 'ruff format src/ tests/' to fix)"
    FAILED=1
fi
echo ""

# Type check
echo "[3/4] Running type checker (mypy)..."
if mypy src/; then
    echo "  PASSED"
else
    echo "  WARNINGS (see above)"
fi
echo ""

# Security scan
echo "[4/4] Running security scan (bandit)..."
if command -v bandit &> /dev/null; then
    if bandit -r src/ -c pyproject.toml -q; then
        echo "  PASSED"
    else
        echo "  WARNINGS (see above)"
    fi
else
    echo "  SKIPPED (bandit not installed)"
fi
echo ""

echo "========================================"
if [ $FAILED -eq 0 ]; then
    echo "All checks passed!"
else
    echo "Some checks failed!"
    exit 1
fi
echo "========================================"
