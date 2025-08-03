"""
Basic functionality tests for token optimizer components
"""

import sys
from pathlib import Path

import pytest

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "token-optimizer"))


class TestBasicFunctionality:
    """Test basic functionality of the pipeline"""

    def test_imports(self):
        """Test that main modules can be imported"""
        try:
            from pipeline import TokenOptimizationPipeline

            assert TokenOptimizationPipeline is not None
        except ImportError as e:
            pytest.fail(f"Failed to import pipeline: {e}")

    def test_config_loading(self, temp_config_file):
        """Test configuration loading"""
        from pipeline import TokenOptimizationPipeline

        pipeline = TokenOptimizationPipeline(config_path=str(temp_config_file))
        assert pipeline.config is not None
        assert "tokenizer" in pipeline.config
        assert "pipeline" in pipeline.config

    def test_sample_text_processing(self, sample_text, temp_config_file, monkeypatch):
        """Test basic text processing"""
        from pipeline import TokenOptimizationPipeline

        # Mock subprocess to avoid running actual scripts
        def mock_run(*args, **kwargs):
            class Result:
                returncode = 0
                stdout = kwargs.get("input", "").replace("please", "").replace("could you", "")
                stderr = "Mock processing complete"

            return Result()

        import subprocess

        monkeypatch.setattr(subprocess, "run", mock_run)

        pipeline = TokenOptimizationPipeline(config_path=str(temp_config_file))

        # Test stage processing with a valid stage name
        result = pipeline.run_stage("spell_check", "01_spell_check.py", sample_text)
        assert len(result) <= len(sample_text)  # Should be shorter or same

    def test_abbreviations_dict_structure(self, abbreviations_dict):
        """Test abbreviations dictionary structure"""
        assert isinstance(abbreviations_dict, dict)
        assert len(abbreviations_dict) > 0

        # Check some expected abbreviations
        assert abbreviations_dict.get("repository") == "repo"
        assert abbreviations_dict.get("development") == "dev"
        assert abbreviations_dict.get("configuration") == "config"

    def test_test_helpers(self, test_helpers):
        """Test that test helpers work correctly"""
        # Test word counting
        assert test_helpers.count_words("hello world test") == 3

        # Test reduction calculation
        reduction = test_helpers.calculate_reduction("hello world", "hi")
        assert 0 <= reduction <= 100

        # Test file creation
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            path = test_helpers.create_test_file(f.name, "test content")
            assert Path(path).exists()
            Path(path).unlink()  # Clean up

    def test_pipeline_stages_config(self, temp_config_file):
        """Test pipeline stages configuration"""
        import yaml

        with open(temp_config_file) as f:
            config = yaml.safe_load(f)

        # Check all expected stages
        expected_stages = ["spell_check", "abbreviations", "token_aware", "ml_paraphrase"]
        for stage in expected_stages:
            assert stage in config["pipeline"]
            assert "enabled" in config["pipeline"][stage]

    def test_empty_input_handling(self, temp_config_file, monkeypatch):
        """Test handling of empty input"""
        from pipeline import TokenOptimizationPipeline

        # Mock subprocess
        def mock_run(*args, **kwargs):
            class Result:
                returncode = 0
                stdout = kwargs.get("input", "")
                stderr = ""

            return Result()

        import subprocess

        monkeypatch.setattr(subprocess, "run", mock_run)

        pipeline = TokenOptimizationPipeline(config_path=str(temp_config_file))

        # Test with empty string
        result = pipeline.run_stage("spell_check", "01_spell_check.py", "")
        assert result == ""

        # Test with whitespace
        result = pipeline.run_stage("spell_check", "01_spell_check.py", "   ")
        assert result.strip() == ""
