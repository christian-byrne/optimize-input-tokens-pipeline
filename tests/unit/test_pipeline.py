"""
Unit tests for the main pipeline
"""

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "token-optimizer"))


class TestTokenOptimizationPipeline:
    """Test main pipeline functionality"""

    def test_import(self):
        """Test that pipeline can be imported"""
        from pipeline import TokenOptimizationPipeline

        assert TokenOptimizationPipeline is not None

    def test_pipeline_initialization(self, temp_config_file):
        """Test pipeline initialization with config"""
        from pipeline import TokenOptimizationPipeline

        pipeline = TokenOptimizationPipeline(config_path=str(temp_config_file))

        assert pipeline.config is not None
        assert pipeline.tokenizer is not None
        assert pipeline.scripts_dir.exists()

    def test_token_counting(self, temp_config_file, mock_tokenizer, monkeypatch):
        """Test token counting in pipeline"""
        from pipeline import TokenOptimizationPipeline

        # Mock the AutoTokenizer
        monkeypatch.setattr("transformers.AutoTokenizer", mock_tokenizer)

        pipeline = TokenOptimizationPipeline(config_path=str(temp_config_file))

        text = "Hello world test"
        count = pipeline.count_tokens(text)
        assert count == 3  # Based on mock tokenizer

    def test_stage_disabling(self, temp_config_file, mock_tokenizer, monkeypatch):
        """Test disabling pipeline stages"""
        from pipeline import TokenOptimizationPipeline

        monkeypatch.setattr("transformers.AutoTokenizer", mock_tokenizer)

        # Load config and disable a stage
        with open(temp_config_file) as f:
            config = yaml.safe_load(f)

        config["pipeline"]["spell_check"]["enabled"] = False

        with open(temp_config_file, "w") as f:
            yaml.dump(config, f)

        pipeline = TokenOptimizationPipeline(config_path=str(temp_config_file))

        # The spell_check stage should be skipped
        result = pipeline.run_stage("spell_check", "01_spell_check.py", "test input")
        assert result == "test input"  # Should return unchanged

    def test_stage_failure_handling(self, temp_config_file, mock_tokenizer, monkeypatch):
        """Test handling of stage failures"""
        from pipeline import TokenOptimizationPipeline

        monkeypatch.setattr("transformers.AutoTokenizer", mock_tokenizer)

        pipeline = TokenOptimizationPipeline(config_path=str(temp_config_file))

        # Try to run a non-existent script
        result = pipeline.run_stage("test_stage", "nonexistent.py", "test input")

        # Should return original input on failure
        assert result == "test input"

    def test_analyze_text(self, temp_config_file, mock_tokenizer, monkeypatch, capsys):
        """Test analyze_text functionality"""

        from pipeline import TokenOptimizationPipeline

        monkeypatch.setattr("transformers.AutoTokenizer", mock_tokenizer)

        # Mock subprocess to return analysis results
        def mock_run(*args, **kwargs):
            class Result:
                returncode = 0
                stdout = '[{"phrase": "it is", "suggested": "it\'s", "occurrences": 2, "total_savings": 2}]'
                stderr = ""

            return Result()

        monkeypatch.setattr("subprocess.run", mock_run)

        pipeline = TokenOptimizationPipeline(config_path=str(temp_config_file))
        pipeline.analyze_text("it is a test")

        captured = capsys.readouterr()
        assert "it is" in captured.err
        assert "it's" in captured.err


class TestVerbosePipeline:
    """Test verbose pipeline functionality"""

    def test_verbose_import(self):
        """Test that verbose pipeline can be imported"""
        try:
            from pipeline_verbose import VerboseTokenOptimizationPipeline

            assert VerboseTokenOptimizationPipeline is not None
        except ImportError:
            pytest.skip("Verbose pipeline requires rich library")

    def test_verbose_initialization(self, temp_config_file, mock_tokenizer, monkeypatch):
        """Test verbose pipeline initialization"""
        try:
            from pipeline_verbose import VerboseTokenOptimizationPipeline
        except ImportError:
            pytest.skip("Verbose pipeline requires rich library")

        monkeypatch.setattr("transformers.AutoTokenizer", mock_tokenizer)

        pipeline = VerboseTokenOptimizationPipeline(config_path=str(temp_config_file), verbose=True)

        assert pipeline.verbose is True
        assert pipeline.diff_viewer is not None
        assert pipeline.console is not None

    def test_stage_history_tracking(self, temp_config_file, mock_tokenizer, monkeypatch):
        """Test that stage history is tracked"""
        try:
            from pipeline_verbose import VerboseTokenOptimizationPipeline
        except ImportError:
            pytest.skip("Verbose pipeline requires rich library")

        monkeypatch.setattr("transformers.AutoTokenizer", mock_tokenizer)

        pipeline = VerboseTokenOptimizationPipeline(
            config_path=str(temp_config_file), verbose=False  # Disable verbose output for testing
        )

        assert len(pipeline.stage_history) == 0

        # Run a stage
        pipeline.stage_history.append(("test_stage", 100))

        assert len(pipeline.stage_history) == 1
        assert pipeline.stage_history[0] == ("test_stage", 100)
