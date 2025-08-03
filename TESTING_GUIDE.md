# Testing Guide for LLM Cost Optimization

## Overview

This project includes a comprehensive testing framework with:
- Unit tests for individual components
- Integration tests for the full pipeline
- CI/CD scripts for automated quality checks
- Code formatting and linting with Black and Ruff

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures and helpers
├── helpers.py                  # Import helpers for scripts
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_spell_check.py    # SpellChecker tests
│   ├── test_abbreviations.py   # AbbreviationReplacer tests
│   ├── test_token_aware.py     # TokenAwareOptimizer tests
│   ├── test_pipeline.py        # Pipeline tests
│   └── test_basic_functionality.py  # Basic functionality tests
└── integration/                # Integration tests
    ├── __init__.py
    └── test_full_pipeline.py   # End-to-end tests
```

## Running Tests

### Quick Start
```bash
# Run basic tests
./run_tests.sh
```

### Using Make
```bash
# Run all CI checks
make ci

# Individual commands
make ci-format    # Format code with Black and Ruff
make ci-lint      # Lint with Ruff and Flake8
make ci-typecheck # Type check with mypy
make ci-test      # Run pytest with coverage
```

### Using Pytest Directly
```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=token_optimizer

# Run specific test file
pytest tests/unit/test_abbreviations.py

# Run specific test
pytest tests/unit/test_basic_functionality.py::TestBasicFunctionality::test_imports

# Run with verbose output
pytest -v

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/ -m integration
```

## Test Fixtures

The `conftest.py` file provides useful fixtures:

- `sample_text`: Short sample text for testing
- `long_sample_text`: Longer text with more optimization opportunities
- `abbreviations_dict`: Test abbreviations dictionary
- `temp_dir`: Temporary directory for test files
- `temp_config_file`: Temporary pipeline configuration
- `temp_abbreviations_file`: Temporary abbreviations JSON
- `mock_tokenizer`: Mock tokenizer for testing without models
- `test_helpers`: Helper methods for tests

## Writing New Tests

### Example Unit Test
```python
def test_my_feature(sample_text, test_helpers):
    """Test description"""
    # Arrange
    input_text = sample_text
    
    # Act
    result = my_function(input_text)
    
    # Assert
    assert len(result) < len(input_text)
    reduction = test_helpers.calculate_reduction(input_text, result)
    assert reduction > 20  # At least 20% reduction
```

### Example Integration Test
```python
@pytest.mark.integration
def test_full_pipeline(long_sample_text, temp_dir):
    """Test full pipeline processing"""
    # Create input file
    input_file = temp_dir / "input.txt"
    input_file.write_text(long_sample_text)
    
    # Run pipeline
    result = subprocess.run([...])
    
    # Verify results
    assert result.returncode == 0
```

## CI/CD Scripts

Located in `scripts/`:

1. **ci_format.sh** - Code formatting with Black and Ruff
2. **ci_lint.sh** - Linting with Ruff and Flake8
3. **ci_typecheck.sh** - Type checking with mypy
4. **ci_test.sh** - Test execution with pytest
5. **ci_all.sh** - Run all checks in sequence

## Code Quality Tools

### Ruff Configuration
See `ruff.toml` for detailed configuration. Key features:
- Comprehensive rule sets enabled
- Line length: 100 characters
- Compatible with Black formatting
- Excludes test files from documentation requirements

### Black Configuration
- Line length: 100 characters
- Target Python 3.8+
- Configured in `pyproject.toml`

### Coverage Configuration
See `.coveragerc`:
- Minimum coverage: Aim for 80%+
- HTML reports in `htmlcov/`
- Excludes test files and virtual environment

## Continuous Integration

### GitHub Actions
See `.github/workflows/ci.yml`:
- Tests on Python 3.8, 3.9, 3.10, 3.11
- Runs all quality checks
- Uploads coverage to Codecov

### Pre-commit Checks
Before committing:
```bash
make check  # Runs format, lint, and test
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure virtual environment is activated
   - Run `pip install -e .` to install package in development mode

2. **Missing Dependencies**
   - Run `pip install -r requirements.txt`
   - For spaCy: `python -m spacy download en_core_web_sm`

3. **Test Failures**
   - Check if models are downloaded
   - Verify paths in test configuration
   - Run with `-v` for verbose output

### Debug Mode
```bash
# Run tests with debugging
pytest -v -s --tb=short

# Run specific test with print statements
pytest path/to/test.py::TestClass::test_method -s
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Use Fixtures**: Leverage pytest fixtures for setup
3. **Mock External Dependencies**: Use monkeypatch for external calls
4. **Test Edge Cases**: Empty input, large input, special characters
5. **Document Tests**: Clear docstrings explaining what's tested
6. **Fast Tests**: Unit tests should run in < 1 second each