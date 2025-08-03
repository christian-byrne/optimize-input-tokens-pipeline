#!/bin/bash
# CI script for code formatting

set -e  # Exit on error

echo "🎨 Running code formatters..."
echo "=============================="

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌ Error: Virtual environment not activated"
    echo "Please run: source venv/bin/activate"
    exit 1
fi

# Change to project root
cd "$(dirname "$0")/.."

# Run black formatter
echo "Running Black..."
black token-optimizer/ tests/ --line-length 100

# Run isort for import sorting
echo "Running isort..."
python -m isort token-optimizer/ tests/ --profile black --line-length 100

# Run ruff formatter
echo "Running Ruff formatter..."
ruff format token-optimizer/ tests/

echo
echo "✅ Formatting complete!"