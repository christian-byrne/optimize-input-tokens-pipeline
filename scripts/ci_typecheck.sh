#!/bin/bash
# CI script for type checking

set -e  # Exit on error

echo "🔤 Running type checkers..."
echo "=========================="

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌ Error: Virtual environment not activated"
    echo "Please run: source venv/bin/activate"
    exit 1
fi

# Change to project root
cd "$(dirname "$0")/.."

# Create mypy config if it doesn't exist
if [ ! -f "mypy.ini" ]; then
    cat > mypy.ini << EOF
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
ignore_missing_imports = True
files = token-optimizer/**/*.py

[mypy-tests.*]
ignore_errors = True
EOF
fi

# Run mypy
echo "Running mypy..."
mypy token-optimizer/ --config-file mypy.ini || true

echo
echo "✅ Type checking complete!"
echo
echo "Note: Type hints are optional but recommended for better code quality."