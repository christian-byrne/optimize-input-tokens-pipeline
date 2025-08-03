#!/bin/bash
# CI script for linting

set -e  # Exit on error

echo "🔍 Running linters..."
echo "===================="

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌ Error: Virtual environment not activated"
    echo "Please run: source venv/bin/activate"
    exit 1
fi

# Change to project root
cd "$(dirname "$0")/.."

# Run ruff linter
echo "Running Ruff linter..."
ruff check token-optimizer/ tests/ || true

# Run flake8
echo
echo "Running Flake8..."
flake8 token-optimizer/ tests/ --max-line-length=100 --exclude=venv,__pycache__ || true

# Run pylint (optional, more strict)
# echo
# echo "Running Pylint..."
# pylint token-optimizer/ tests/ --max-line-length=100 || true

echo
echo "✅ Linting complete!"
echo
echo "To fix issues automatically, run:"
echo "  ruff check --fix token-optimizer/ tests/"