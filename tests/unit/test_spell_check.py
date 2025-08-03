"""
Unit tests for spell checking module
"""

import sys
from pathlib import Path

# Add token-optimizer to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "token-optimizer"))


class TestSpellChecker:
    """Test spell checker functionality"""

    def test_import(self):
        """Test that module can be imported"""
        from scripts.spell_check import SpellChecker
        assert SpellChecker is not None

    def test_basic_correction(self):
        """Test basic spelling correction"""
        from scripts.spell_check import SpellChecker

        checker = SpellChecker(max_edit_distance=2)

        # Test single word corrections
        test_cases = [
            ("helllo", "hello"),
            ("wrold", "world"),
            ("recieve", "receive"),
            ("occured", "occurred"),
            ("seperate", "separate")
        ]

        for misspelled, expected in test_cases:
            result = checker.correct_text(misspelled)
            assert expected in result.lower(), \
                f"Expected '{expected}' in result for '{misspelled}', got '{result}'"

    def test_preserve_case(self):
        """Test that original case is preserved"""
        from scripts.spell_check import SpellChecker

        checker = SpellChecker()

        test_cases = [
            ("Helllo", "Hello"),
            ("WROLD", "WORLD"),
            ("ReCieVe", "Receive")
        ]

        for misspelled, expected in test_cases:
            result = checker.correct_text(misspelled)
            # Check first letter case is preserved
            assert result[0].isupper() == expected[0].isupper(), \
                f"Case not preserved for '{misspelled}'"

    def test_skip_urls_and_paths(self):
        """Test that URLs and paths are not corrected"""
        from scripts.spell_check import SpellChecker

        checker = SpellChecker()

        test_cases = [
            "https://github.com/user/repo",
            "/usr/local/bin/python",
            "user@example.com",
            "config.yaml",
            "${VARIABLE}",
            "function_name()",
            "[array_index]"
        ]

        for text in test_cases:
            result = checker.correct_text(text)
            assert result == text, f"URL/path '{text}' was modified to '{result}'"

    def test_preserve_code_blocks(self):
        """Test that code blocks are preserved"""
        from scripts.spell_check import SpellChecker

        checker = SpellChecker()

        text = """
        Here is some text with a typo: recieve
        
        ```python
        def recieve_data():  # This should not be corrected
            return "data"
        ```
        
        More text with typo: occured
        """

        result = checker.correct_text(text)

        # Check that typo outside code block is corrected
        assert "receive" in result
        assert "occurred" in result

        # Check that code block content is preserved
        assert "def recieve_data():" in result

    def test_handle_punctuation(self):
        """Test handling of punctuation"""
        from scripts.spell_check import SpellChecker

        checker = SpellChecker()

        test_cases = [
            ("helllo, world!", "hello, world!"),
            ("The wrold.", "The world."),
            ("(recieve)", "(receive)"),
            ("'occured'", "'occurred'"),
            ('"seperate"', '"separate"')
        ]

        for misspelled, expected in test_cases:
            result = checker.correct_text(misspelled)
            assert result == expected, f"Expected '{expected}', got '{result}'"

    def test_multiple_corrections_in_line(self):
        """Test multiple corrections in a single line"""
        from scripts.spell_check import SpellChecker

        checker = SpellChecker()

        text = "Helllo wrold, I recieved your mesage"
        result = checker.correct_text(text)

        assert "Hello" in result
        assert "world" in result
        assert "received" in result
        assert "message" in result

    def test_empty_input(self):
        """Test handling of empty input"""
        from scripts.spell_check import SpellChecker

        checker = SpellChecker()

        assert checker.correct_text("") == ""
        assert checker.correct_text("   ") == "   "
        assert checker.correct_text("\n\n") == "\n\n"

    def test_max_edit_distance(self):
        """Test max edit distance parameter"""
        from scripts.spell_check import SpellChecker

        # Strict checker (distance=1)
        strict_checker = SpellChecker(max_edit_distance=1)

        # Should not correct words with distance > 1
        text = "hellooo"  # distance 2 from "hello"
        result = strict_checker.correct_text(text)
        assert result == text  # Should remain unchanged

        # Lenient checker (distance=2)
        lenient_checker = SpellChecker(max_edit_distance=2)
        result = lenient_checker.correct_text(text)
        assert "hello" in result.lower()  # Should be corrected
