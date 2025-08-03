#!/bin/bash
# Quick test runner to verify setup

echo "🧪 Running Token Optimizer Tests"
echo "================================"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Setting up virtual environment..."
    ./setup_project.sh
fi

# Activate venv
source venv/bin/activate

# Install/upgrade test dependencies
pip install -q --upgrade pytest pytest-cov

# Run basic tests
echo
echo "Running basic functionality tests..."
pytest tests/unit/test_basic_functionality.py -v

# Run a simple pipeline test
echo
echo "Testing pipeline with sample text..."
cd token-optimizer
echo "Please help me understand the repository configuration" | python pipeline.py

echo
echo "✅ Basic tests complete!"
echo
echo "To run all tests: make ci-test"
echo "To run all CI checks: make ci"