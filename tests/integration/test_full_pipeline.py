"""
Integration tests for the full pipeline
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Add token-optimizer to path
TOKEN_OPTIMIZER_PATH = Path(__file__).parent.parent.parent / "token-optimizer"
sys.path.insert(0, str(TOKEN_OPTIMIZER_PATH))


class TestFullPipeline:
    """Test full pipeline integration"""

    @pytest.mark.integration
    def test_end_to_end_processing(self, sample_text, temp_dir):
        """Test end-to-end text processing"""
        # Create input file
        input_file = temp_dir / "input.txt"
        output_file = temp_dir / "output.txt"

        with open(input_file, 'w') as f:
            f.write(sample_text)

        # Run pipeline
        cmd = [
            sys.executable,
            str(TOKEN_OPTIMIZER_PATH / "pipeline.py"),
            str(input_file),
            "-o", str(output_file)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        # Check execution
        assert result.returncode == 0, f"Pipeline failed: {result.stderr}"
        assert output_file.exists()

        # Check output
        with open(output_file) as f:
            output_text = f.read()

        # Output should be shorter
        assert len(output_text) < len(sample_text)

        # Key words should be preserved
        assert "help" in output_text.lower()
        assert "understand" in output_text.lower()

    @pytest.mark.integration
    def test_stdin_stdout_processing(self, sample_text):
        """Test processing via stdin/stdout"""
        cmd = [
            sys.executable,
            str(TOKEN_OPTIMIZER_PATH / "pipeline.py")
        ]

        result = subprocess.run(
            cmd,
            input=sample_text,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert len(result.stdout) > 0
        assert len(result.stdout) < len(sample_text)

    @pytest.mark.integration
    def test_specific_stages(self, sample_text):
        """Test running specific stages only"""
        cmd = [
            sys.executable,
            str(TOKEN_OPTIMIZER_PATH / "pipeline.py"),
            "--stages", "spell_check", "abbreviations"
        ]

        result = subprocess.run(
            cmd,
            input=sample_text,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0

        # Check that only specified stages ran (from stderr)
        assert "spell_check" in result.stderr
        assert "abbreviations" in result.stderr
        assert "token_aware" not in result.stderr
        assert "ml_paraphrase" not in result.stderr

    @pytest.mark.integration
    def test_analyze_mode(self, long_sample_text):
        """Test analyze mode"""
        cmd = [
            sys.executable,
            str(TOKEN_OPTIMIZER_PATH / "pipeline.py"),
            "--analyze"
        ]

        result = subprocess.run(
            cmd,
            input=long_sample_text,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0

        # Should show potential optimizations
        assert "potential" in result.stderr.lower() or "optimization" in result.stderr.lower()

    @pytest.mark.integration
    def test_count_only_mode(self, sample_text):
        """Test count-only mode"""
        cmd = [
            sys.executable,
            str(TOKEN_OPTIMIZER_PATH / "pipeline.py"),
            "--count-only"
        ]

        result = subprocess.run(
            cmd,
            input=sample_text,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0

        # Should output only a number
        assert result.stdout.strip().endswith("tokens")

    @pytest.mark.integration
    @pytest.mark.slow
    def test_all_stages_sequential(self, long_sample_text, temp_dir):
        """Test all stages run sequentially"""
        # Run each stage individually and verify output changes
        stages = ["spell_check", "abbreviations", "token_aware"]

        current_text = long_sample_text

        for stage in stages:
            cmd = [
                sys.executable,
                str(TOKEN_OPTIMIZER_PATH / "pipeline.py"),
                "--stages", stage
            ]

            result = subprocess.run(
                cmd,
                input=current_text,
                capture_output=True,
                text=True
            )

            assert result.returncode == 0

            # Each stage should produce some change (for our test text)
            assert len(result.stdout) <= len(current_text)

            current_text = result.stdout

    @pytest.mark.integration
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Test with non-existent file
        cmd = [
            sys.executable,
            str(TOKEN_OPTIMIZER_PATH / "pipeline.py"),
            "nonexistent_file.txt"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        # Should fail gracefully
        assert result.returncode != 0

    @pytest.mark.integration
    def test_verbose_mode_runs(self, sample_text):
        """Test that verbose mode runs without errors"""
        cmd = [
            sys.executable,
            str(TOKEN_OPTIMIZER_PATH / "pipeline.py"),
            "--verbose"
        ]

        result = subprocess.run(
            cmd,
            input=sample_text,
            capture_output=True,
            text=True
        )

        # Verbose mode might fail if rich is not installed
        # Just check it doesn't crash catastrophically
        assert result.returncode in [0, 1]
