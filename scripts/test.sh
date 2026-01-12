#!/usr/bin/env bash
# NewsDigest Test Script
# Runs the test suite

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Parse arguments
COVERAGE=false
VERBOSE=false
TEST_PATH="tests/"

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS] [TEST_PATH]"
            echo ""
            echo "Options:"
            echo "  -c, --coverage    Run with coverage reporting"
            echo "  -v, --verbose     Verbose output"
            echo "  -h, --help        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                      # Run all tests"
            echo "  $0 -c                   # Run with coverage"
            echo "  $0 tests/unit/          # Run unit tests only"
            echo "  $0 -v tests/integration # Run integration tests verbosely"
            exit 0
            ;;
        *)
            TEST_PATH="$1"
            shift
            ;;
    esac
done

echo "========================================"
echo "NewsDigest Test Suite"
echo "========================================"
echo ""

cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Build pytest arguments
PYTEST_ARGS=()

if [ "$VERBOSE" = true ]; then
    PYTEST_ARGS+=("-v")
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_ARGS+=("--cov=src/newsdigest" "--cov-report=html" "--cov-report=term")
fi

PYTEST_ARGS+=("$TEST_PATH")

# Run tests
echo "Running: pytest ${PYTEST_ARGS[*]}"
echo ""

pytest "${PYTEST_ARGS[@]}"

echo ""
echo "========================================"
echo "Tests complete!"
echo "========================================"

if [ "$COVERAGE" = true ]; then
    echo ""
    echo "Coverage report generated in htmlcov/"
fi
