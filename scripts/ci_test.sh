#!/bin/bash
# CI script for running tests

set -e  # Exit on error

echo "🧪 Running tests..."
echo "=================="

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌ Error: Virtual environment not activated"
    echo "Please run: source venv/bin/activate"
    exit 1
fi

# Change to project root
cd "$(dirname "$0")/.."

# Install test dependencies if needed
pip install -q pytest pytest-cov

# Run unit tests with coverage
echo "Running unit tests..."
pytest tests/unit/ -v --cov=token_optimizer --cov-report=term-missing

# Run integration tests (marked as integration)
echo
echo "Running integration tests..."
pytest tests/integration/ -v -m integration || true

# Generate coverage report
echo
echo "Generating coverage report..."
pytest tests/ --cov=token_optimizer --cov-report=html --cov-report=term

echo
echo "✅ Testing complete!"
echo
echo "Coverage report available at: htmlcov/index.html"