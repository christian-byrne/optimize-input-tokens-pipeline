"""
Unit tests for token-aware optimization module
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "token-optimizer"))


class TestTokenAwareOptimizer:
    """Test token-aware optimizer functionality"""

    def test_import(self):
        """Test that module can be imported"""
        from scripts.token_aware import TokenAwareOptimizer
        assert TokenAwareOptimizer is not None

    def test_token_counting(self, mock_tokenizer, monkeypatch):
        """Test token counting functionality"""
        from scripts.token_aware import TokenAwareOptimizer

        # Mock the AutoTokenizer
        monkeypatch.setattr("scripts.token_aware.AutoTokenizer", mock_tokenizer)

        optimizer = TokenAwareOptimizer(model_name='gpt2')

        # Test counting
        count = optimizer._count_tokens("hello world test")
        assert count == 3  # Based on our mock tokenizer

    def test_contraction_replacements(self, mock_tokenizer, monkeypatch):
        """Test contraction replacements"""
        from scripts.token_aware import TokenAwareOptimizer

        monkeypatch.setattr("scripts.token_aware.AutoTokenizer", mock_tokenizer)

        optimizer = TokenAwareOptimizer(model_name='gpt2', min_savings=1)

        test_cases = [
            ("it is", "it's"),
            ("you are", "you're"),
            ("do not", "don't"),
            ("cannot", "can't"),
            ("will not", "won't")
        ]

        for original, expected in test_cases:
            text = f"I think {original} important"
            result, stats = optimizer.optimize_text(text)
            assert expected in result.lower(), \
                f"Expected '{expected}' in result for '{original}'"

    def test_min_savings_threshold(self, mock_tokenizer, monkeypatch):
        """Test minimum savings threshold"""
        from scripts.token_aware import TokenAwareOptimizer

        # Create a mock tokenizer that gives specific token counts
        class CustomMockTokenizer:
            def encode(self, text, add_special_tokens=False):
                # Make "it is" = 2 tokens, "it's" = 2 tokens (no savings)
                if text == "it is" or text == "it's":
                    return [1, 2]
                return list(range(len(text.split())))

            @classmethod
            def from_pretrained(cls, model_name):
                return cls()

        monkeypatch.setattr("scripts.token_aware.AutoTokenizer", CustomMockTokenizer)

        optimizer = TokenAwareOptimizer(model_name='gpt2', min_savings=1)

        text = "it is a test"
        result, stats = optimizer.optimize_text(text)

        # Should not replace since savings = 0
        assert "it is" in result
        assert "it's" not in result

    def test_case_preservation(self, mock_tokenizer, monkeypatch):
        """Test that case is preserved in replacements"""
        from scripts.token_aware import TokenAwareOptimizer

        monkeypatch.setattr("scripts.token_aware.AutoTokenizer", mock_tokenizer)

        optimizer = TokenAwareOptimizer(model_name='gpt2')

        test_cases = [
            ("It Is", "It's"),
            ("YOU ARE", "YOU'RE"),
            ("Do Not", "Don't")
        ]

        for original, expected_pattern in test_cases:
            result, _ = optimizer.optimize_text(original)
            # Check that first letter case is preserved
            assert result[0].isupper() == original[0].isupper()

    def test_empty_replacements(self, mock_tokenizer, monkeypatch):
        """Test handling of empty replacements"""
        from scripts.token_aware import TokenAwareOptimizer

        monkeypatch.setattr("scripts.token_aware.AutoTokenizer", mock_tokenizer)

        optimizer = TokenAwareOptimizer(model_name='gpt2')

        text = "This is basically just a test"
        result, _ = optimizer.optimize_text(text)

        # "basically" and "just" can be removed
        assert "basically" not in result or "just" not in result

    def test_optimization_stats(self, mock_tokenizer, monkeypatch):
        """Test that optimization statistics are correct"""
        from scripts.token_aware import TokenAwareOptimizer

        monkeypatch.setattr("scripts.token_aware.AutoTokenizer", mock_tokenizer)

        optimizer = TokenAwareOptimizer(model_name='gpt2')

        text = "it is important that you are aware"
        result, stats = optimizer.optimize_text(text)

        assert 'total_tokens_saved' in stats
        assert 'replacements' in stats
        assert 'original_tokens' in stats
        assert 'optimized_tokens' in stats
        assert stats['total_tokens_saved'] >= 0

    def test_analyze_mode(self, mock_tokenizer, monkeypatch):
        """Test analyze mode without applying changes"""
        from scripts.token_aware import TokenAwareOptimizer

        monkeypatch.setattr("scripts.token_aware.AutoTokenizer", mock_tokenizer)

        optimizer = TokenAwareOptimizer(model_name='gpt2')

        text = "it is very important that you are here"
        optimizations = optimizer.analyze_text(text)

        assert isinstance(optimizations, list)

        # Should find potential optimizations
        phrases = [opt['phrase'] for opt in optimizations]
        assert any(phrase in ["it is", "you are", "very"] for phrase in phrases)

    def test_technical_shortcuts(self, mock_tokenizer, monkeypatch):
        """Test technical term shortcuts"""
        from scripts.token_aware import TokenAwareOptimizer

        monkeypatch.setattr("scripts.token_aware.AutoTokenizer", mock_tokenizer)

        optimizer = TokenAwareOptimizer(model_name='gpt2')

        test_cases = [
            ("version 2.0", "v 2.0"),
            ("for example", "e.g."),
            ("that is", "i.e."),
            ("versus", "vs"),
            ("number 5", "# 5")
        ]

        for original, expected_pattern in test_cases:
            text = f"The {original} shows this"
            result, _ = optimizer.optimize_text(text)
            # Check if optimization was applied
            assert len(result) <= len(text)

    def test_whole_word_matching(self, mock_tokenizer, monkeypatch):
        """Test that replacements only match whole words"""
        from scripts.token_aware import TokenAwareOptimizer

        monkeypatch.setattr("scripts.token_aware.AutoTokenizer", mock_tokenizer)

        optimizer = TokenAwareOptimizer(model_name='gpt2')

        # Should not replace parts of words
        text = "The donut shop is open"
        result, _ = optimizer.optimize_text(text)

        # "donut" should not become "don'tut"
        assert "donut" in result or "don'tut" not in result

    def test_multiple_optimizations(self, mock_tokenizer, monkeypatch):
        """Test multiple optimizations in one text"""
        from scripts.token_aware import TokenAwareOptimizer

        monkeypatch.setattr("scripts.token_aware.AutoTokenizer", mock_tokenizer)

        optimizer = TokenAwareOptimizer(model_name='gpt2')

        text = "It is important that you are aware. Do not forget this."
        result, stats = optimizer.optimize_text(text)

        # Should have multiple replacements
        assert len(stats['replacements']) >= 2
        assert stats['total_tokens_saved'] > 0
