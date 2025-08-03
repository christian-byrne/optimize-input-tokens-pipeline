#!/bin/bash
# Run all CI checks

set -e  # Exit on error

echo "🚀 Running all CI checks..."
echo "=========================="
echo

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌ Error: Virtual environment not activated"
    echo "Please run: source venv/bin/activate"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Run all checks
echo "1️⃣ Formatting..."
"$SCRIPT_DIR/ci_format.sh"
echo

echo "2️⃣ Linting..."
"$SCRIPT_DIR/ci_lint.sh"
echo

echo "3️⃣ Type checking..."
"$SCRIPT_DIR/ci_typecheck.sh"
echo

echo "4️⃣ Testing..."
"$SCRIPT_DIR/ci_test.sh"
echo

echo "✅ All CI checks complete!"
echo
echo "Summary:"
echo "  - Code formatted ✓"
echo "  - Linting passed ✓"
echo "  - Type checking done ✓"
echo "  - Tests executed ✓"