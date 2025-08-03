"""
Unit tests for abbreviations module
"""

import sys
from pathlib import Path

# Add token-optimizer directory to path
token_optimizer_path = Path(__file__).parent.parent.parent / "token-optimizer"
sys.path.insert(0, str(token_optimizer_path))


class TestAbbreviationReplacer:
    """Test abbreviation replacer functionality"""

    def test_import(self):
        """Test that module can be imported"""
        import importlib.util
        
        scripts_path = Path(__file__).parent.parent.parent / "token-optimizer/scripts"
        spec = importlib.util.spec_from_file_location("abbreviations", scripts_path / "02_abbreviations.py")
        abbreviations = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(abbreviations)
        
        assert abbreviations.AbbreviationReplacer is not None

    def test_basic_replacements(self, temp_abbreviations_file):
        """Test basic abbreviation replacements"""
        import importlib.util
        scripts_path = Path(__file__).parent.parent.parent / "token-optimizer/scripts"
        spec = importlib.util.spec_from_file_location("abbreviations", scripts_path / "02_abbreviations.py")
        abbreviations = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(abbreviations)
        AbbreviationReplacer = abbreviations.AbbreviationReplacer

        replacer = AbbreviationReplacer(config_path=str(temp_abbreviations_file))

        text = "Please help me with the repository development configuration"
        result, stats = replacer.replace_abbreviations(text)

        assert "repo" in result
        assert "dev" in result
        assert "config" in result
        assert "repository" not in result
        assert "development" not in result

    def test_case_preservation(self, temp_abbreviations_file):
        """Test that case is preserved for single words"""
        import importlib.util
        scripts_path = Path(__file__).parent.parent.parent / "token-optimizer/scripts"
        spec = importlib.util.spec_from_file_location("abbreviations", scripts_path / "02_abbreviations.py")
        abbreviations = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(abbreviations)
        AbbreviationReplacer = abbreviations.AbbreviationReplacer

        replacer = AbbreviationReplacer(config_path=str(temp_abbreviations_file))

        test_cases = [
            ("Repository", "Repo"),
            ("DEVELOPMENT", "DEV"),
            ("Configuration", "Config")
        ]

        for original, expected in test_cases:
            result, _ = replacer.replace_abbreviations(original)
            assert expected in result, f"Expected '{expected}' for '{original}', got '{result}'"

    def test_phrase_removal(self, temp_abbreviations_file):
        """Test removal of phrases (empty replacements)"""
        import importlib.util
        scripts_path = Path(__file__).parent.parent.parent / "token-optimizer/scripts"
        spec = importlib.util.spec_from_file_location("abbreviations", scripts_path / "02_abbreviations.py")
        abbreviations = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(abbreviations)
        AbbreviationReplacer = abbreviations.AbbreviationReplacer

        replacer = AbbreviationReplacer(config_path=str(temp_abbreviations_file))

        text = "Please could you help me understand"
        result, _ = replacer.replace_abbreviations(text)

        assert "please" not in result.lower()
        assert "could you" not in result.lower()
        assert "help me understand" in result.lower()

    def test_multi_word_replacements(self, temp_abbreviations_file):
        """Test multi-word phrase replacements"""
        import importlib.util
        scripts_path = Path(__file__).parent.parent.parent / "token-optimizer/scripts"
        spec = importlib.util.spec_from_file_location("abbreviations", scripts_path / "02_abbreviations.py")
        abbreviations = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(abbreviations)
        AbbreviationReplacer = abbreviations.AbbreviationReplacer

        replacer = AbbreviationReplacer(config_path=str(temp_abbreviations_file))

        text = "Thank you very much for your help"
        result, _ = replacer.replace_abbreviations(text)

        assert "thanks" in result.lower()
        assert "thank you very much" not in result.lower()

    def test_replacement_statistics(self, temp_abbreviations_file):
        """Test that replacement statistics are tracked"""
        import importlib.util
        scripts_path = Path(__file__).parent.parent.parent / "token-optimizer/scripts"
        spec = importlib.util.spec_from_file_location("abbreviations", scripts_path / "02_abbreviations.py")
        abbreviations = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(abbreviations)
        AbbreviationReplacer = abbreviations.AbbreviationReplacer

        replacer = AbbreviationReplacer(config_path=str(temp_abbreviations_file))

        text = "Repository repository REPOSITORY development Development"
        result, stats = replacer.replace_abbreviations(text)

        # Find repository replacement in stats
        repo_stats = [s for s in stats if s[0] == "repository"]
        assert len(repo_stats) > 0
        assert repo_stats[0][2] == 3  # Should have 3 replacements

    def test_word_boundaries(self, temp_abbreviations_file):
        """Test that replacements respect word boundaries"""
        import importlib.util
        scripts_path = Path(__file__).parent.parent.parent / "token-optimizer/scripts"
        spec = importlib.util.spec_from_file_location("abbreviations", scripts_path / "02_abbreviations.py")
        abbreviations = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(abbreviations)
        AbbreviationReplacer = abbreviations.AbbreviationReplacer

        replacer = AbbreviationReplacer(config_path=str(temp_abbreviations_file))

        # Should not replace parts of words
        text = "repositoryName developmental preconfiguration"
        result, _ = replacer.replace_abbreviations(text)

        # These should remain unchanged (no word boundary match)
        assert "repositoryName" in result
        assert "developmental" in result
        assert "preconfiguration" in result

    def test_custom_abbreviation(self):
        """Test adding custom abbreviations at runtime"""
        import importlib.util
        scripts_path = Path(__file__).parent.parent.parent / "token-optimizer/scripts"
        spec = importlib.util.spec_from_file_location("abbreviations", scripts_path / "02_abbreviations.py")
        abbreviations = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(abbreviations)
        AbbreviationReplacer = abbreviations.AbbreviationReplacer

        replacer = AbbreviationReplacer()
        replacer.add_custom_abbreviation("artificial intelligence", "AI")

        text = "We use artificial intelligence for processing"
        result, _ = replacer.replace_abbreviations(text)

        assert "AI" in result
        assert "artificial intelligence" not in result

    def test_empty_input(self, temp_abbreviations_file):
        """Test handling of empty input"""
        import importlib.util
        scripts_path = Path(__file__).parent.parent.parent / "token-optimizer/scripts"
        spec = importlib.util.spec_from_file_location("abbreviations", scripts_path / "02_abbreviations.py")
        abbreviations = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(abbreviations)
        AbbreviationReplacer = abbreviations.AbbreviationReplacer

        replacer = AbbreviationReplacer(config_path=str(temp_abbreviations_file))

        result, stats = replacer.replace_abbreviations("")
        assert result == ""
        assert len(stats) == 0

    def test_no_matches(self, temp_abbreviations_file):
        """Test text with no matching abbreviations"""
        import importlib.util
        scripts_path = Path(__file__).parent.parent.parent / "token-optimizer/scripts"
        spec = importlib.util.spec_from_file_location("abbreviations", scripts_path / "02_abbreviations.py")
        abbreviations = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(abbreviations)
        AbbreviationReplacer = abbreviations.AbbreviationReplacer

        replacer = AbbreviationReplacer(config_path=str(temp_abbreviations_file))

        text = "Hello world, this is a test"
        result, stats = replacer.replace_abbreviations(text)

        assert result == text
        assert len(stats) == 0

    def test_punctuation_spacing(self, temp_abbreviations_file):
        """Test that punctuation spacing is fixed after replacements"""
        import importlib.util
        scripts_path = Path(__file__).parent.parent.parent / "token-optimizer/scripts"
        spec = importlib.util.spec_from_file_location("abbreviations", scripts_path / "02_abbreviations.py")
        abbreviations = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(abbreviations)
        AbbreviationReplacer = abbreviations.AbbreviationReplacer

        replacer = AbbreviationReplacer(config_path=str(temp_abbreviations_file))

        text = "Please , could you help ?"
        result, _ = replacer.replace_abbreviations(text)

        # Should fix spacing around punctuation
        assert " ," not in result
        assert " ?" not in result

    def test_missing_config_file(self):
        """Test behavior with missing config file"""
        import importlib.util
        scripts_path = Path(__file__).parent.parent.parent / "token-optimizer/scripts"
        spec = importlib.util.spec_from_file_location("abbreviations", scripts_path / "02_abbreviations.py")
        abbreviations = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(abbreviations)
        AbbreviationReplacer = abbreviations.AbbreviationReplacer

        # Should not crash, just warn
        replacer = AbbreviationReplacer(config_path="nonexistent.json")

        text = "repository development"
        result, _ = replacer.replace_abbreviations(text)

        # Should return original text when no abbreviations loaded
        assert result == text
