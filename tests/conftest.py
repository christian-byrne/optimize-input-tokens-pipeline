"""
Pytest configuration and shared fixtures for all tests
"""

import json
import shutil
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_text():
    """Provide sample text for testing"""
    return """
    Please could you help me understand the repository configuration?
    I would like to know about the development environment setup.
    It is important to note that we have authentication requirements.
    Thank you very much for your assistance.
    """


@pytest.fixture
def long_sample_text():
    """Provide longer sample text with more optimization opportunities"""
    return """
    I would like to request your assistance with understanding the repository structure 
    and configuration. Could you please provide detailed information about the following:
    
    - The development environment setup and configuration
    - Authentication and authorization requirements
    - Database connection parameters and specifications
    - Application deployment procedures and requirements
    
    It is important to note that we have multiple environments including development,
    staging, and production. Each environment has different configurations.
    
    Additionally, I need to understand the dependency management process. The documentation
    mentions specific requirements for initialization and setup procedures.
    
    Thank you very much for your help with this request. Your assistance is greatly
    appreciated.
    """


@pytest.fixture
def abbreviations_dict():
    """Provide test abbreviations dictionary"""
    return {
        "repository": "repo",
        "development": "dev",
        "environment": "env",
        "configuration": "config",
        "authentication": "auth",
        "authorization": "authz",
        "database": "db",
        "application": "app",
        "production": "prod",
        "requirements": "reqs",
        "parameters": "params",
        "specifications": "specs",
        "procedures": "procs",
        "information": "info",
        "documentation": "docs",
        "initialization": "init"
    }


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def temp_config_file(temp_dir):
    """Create a temporary config file"""
    config = {
        "tokenizer": {"model": "gpt2"},
        "pipeline": {
            "spell_check": {"enabled": True, "max_edit_distance": 2},
            "abbreviations": {"enabled": True, "custom_dict_path": "config/abbreviations.json"},
            "token_aware": {"enabled": True, "min_token_savings": 1},
            "ml_paraphrase": {"enabled": True, "model": "t5-small", "max_length_ratio": 0.8}
        },
        "logging": {"level": "INFO", "file": "logs/test.log"},
        "performance": {"batch_size": 32, "cache_enabled": True}
    }

    config_path = temp_dir / "pipeline_config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(config, f)

    return config_path


@pytest.fixture
def temp_abbreviations_file(temp_dir):
    """Create a temporary abbreviations file"""
    abbrevs = {
        "technical_terms": {
            "repository": "repo",
            "development": "dev",
            "configuration": "config"
        },
        "common_phrases": {
            "please": "",
            "could you": "",
            "thank you very much": "thanks"
        }
    }

    abbrev_path = temp_dir / "abbreviations.json"
    with open(abbrev_path, 'w') as f:
        json.dump(abbrevs, f)

    return abbrev_path


@pytest.fixture
def mock_tokenizer():
    """Mock tokenizer for testing without loading models"""
    class MockTokenizer:
        def encode(self, text, add_special_tokens=False):
            # Simple mock: split on spaces and punctuation
            import re
            tokens = re.findall(r'\w+|[^\w\s]', text.lower())
            return list(range(len(tokens)))  # Return dummy token IDs

        def decode(self, token_ids, skip_special_tokens=True):
            # Simple mock decoder
            return " ".join([f"token_{i}" for i in token_ids])

        @classmethod
        def from_pretrained(cls, model_name):
            return cls()

    return MockTokenizer


@pytest.fixture
def sample_pipeline_output():
    """Expected output from pipeline stages"""
    return {
        "spell_check": {
            "input": "Please could you helpp me understand the repositry?",
            "output": "Please could you help me understand the repository?"
        },
        "abbreviations": {
            "input": "Please could you help me understand the repository configuration?",
            "output": "help me understand the repo config?"
        },
        "token_aware": {
            "input": "it is important to note that we have requirements",
            "output": "it's important to note that we have requirements"
        }
    }


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Setup test environment variables"""
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


class TestHelpers:
    """Shared helper methods for tests"""

    @staticmethod
    def count_words(text):
        """Count words in text"""
        return len(text.split())

    @staticmethod
    def calculate_reduction(original, optimized):
        """Calculate percentage reduction"""
        if not original:
            return 0.0
        return (1 - len(optimized) / len(original)) * 100

    @staticmethod
    def create_test_file(path, content):
        """Create a test file with content"""
        with open(path, 'w') as f:
            f.write(content)
        return path

    @staticmethod
    def assert_text_preserved_meaning(original, optimized, min_similarity=0.7):
        """Assert that optimized text preserves meaning (simplified check)"""
        # Simple check: ensure key words are preserved
        import re

        # Extract important words (nouns, verbs)
        important_words = set(re.findall(r'\b[A-Za-z]{4,}\b', original.lower()))
        preserved_words = set(re.findall(r'\b[A-Za-z]{4,}\b', optimized.lower()))

        # Calculate simple similarity
        if not important_words:
            return True

        similarity = len(important_words & preserved_words) / len(important_words)
        assert similarity >= min_similarity, \
            f"Text similarity {similarity:.2f} below threshold {min_similarity}"


@pytest.fixture
def test_helpers():
    """Provide test helper methods"""
    return TestHelpers()
