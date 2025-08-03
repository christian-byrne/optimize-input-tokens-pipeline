#!/usr/bin/env python3
"""
Main Pipeline Orchestrator
Runs all stages of token optimization in sequence
"""

import sys
import argparse
import subprocess
import tempfile
import yaml
import time
from pathlib import Path
from transformers import AutoTokenizer

# Import verbose pipeline if available
try:
    from pipeline_verbose import VerboseTokenOptimizationPipeline

    VERBOSE_AVAILABLE = True
except ImportError:
    VERBOSE_AVAILABLE = False


class TokenOptimizationPipeline:
    def __init__(self, config_path="config/pipeline_config.yaml"):
        # Load configuration
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Initialize tokenizer for measurements
        self.tokenizer = AutoTokenizer.from_pretrained(self.config["tokenizer"]["model"])

        # Set up paths
        self.scripts_dir = Path(__file__).parent / "scripts"

    def count_tokens(self, text):
        """Count tokens in text"""
        return len(self.tokenizer.encode(text, add_special_tokens=False))

    def run_stage(self, stage_name, script_name, input_text, extra_args=None):
        """Run a single pipeline stage"""
        if not self.config["pipeline"][stage_name]["enabled"]:
            print(f"Skipping {stage_name} (disabled in config)", file=sys.stderr)
            return input_text

        script_path = self.scripts_dir / script_name

        # Prepare command
        cmd = [sys.executable, str(script_path)]
        if extra_args:
            cmd.extend(extra_args)

        # Run the script
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd, input=input_text, capture_output=True, text=True, check=True
            )
            elapsed = time.time() - start_time

            output_text = result.stdout

            # Calculate token change
            input_tokens = self.count_tokens(input_text)
            output_tokens = self.count_tokens(output_text)

            print(
                f"✓ {stage_name}: {input_tokens} → {output_tokens} tokens "
                f"(-{input_tokens - output_tokens}, {elapsed:.2f}s)",
                file=sys.stderr,
            )

            return output_text

        except subprocess.CalledProcessError as e:
            print(f"✗ {stage_name} failed: {e.stderr}", file=sys.stderr)
            return input_text  # Return original on failure

    def run_pipeline(self, input_text):
        """Run the full optimization pipeline"""
        print("Starting token optimization pipeline...", file=sys.stderr)
        original_tokens = self.count_tokens(input_text)
        print(f"Original text: {len(input_text)} chars, {original_tokens} tokens", file=sys.stderr)
        print("-" * 50, file=sys.stderr)

        current_text = input_text

        # Stage 1: Spell Check
        if self.config["pipeline"]["spell_check"]["enabled"]:
            current_text = self.run_stage(
                "spell_check",
                "01_spell_check.py",
                current_text,
                ["-d", str(self.config["pipeline"]["spell_check"]["max_edit_distance"])],
            )

        # Stage 2: Abbreviations
        if self.config["pipeline"]["abbreviations"]["enabled"]:
            current_text = self.run_stage(
                "abbreviations",
                "02_abbreviations.py",
                current_text,
                ["-c", self.config["pipeline"]["abbreviations"]["custom_dict_path"]],
            )

        # Stage 3: Token-Aware Replacements
        if self.config["pipeline"]["token_aware"]["enabled"]:
            current_text = self.run_stage(
                "token_aware",
                "03_token_aware.py",
                current_text,
                [
                    "-m",
                    self.config["tokenizer"]["model"],
                    "-s",
                    str(self.config["pipeline"]["token_aware"]["min_token_savings"]),
                ],
            )

        # Stage 4: ML Paraphrasing
        if self.config["pipeline"]["ml_paraphrase"]["enabled"]:
            current_text = self.run_stage(
                "ml_paraphrase",
                "04_ml_paraphrase.py",
                current_text,
                [
                    "-m",
                    self.config["pipeline"]["ml_paraphrase"]["model"],
                    "-r",
                    str(self.config["pipeline"]["ml_paraphrase"]["max_length_ratio"]),
                ],
            )

        # Final statistics
        final_tokens = self.count_tokens(current_text)
        print("-" * 50, file=sys.stderr)
        print(f"Final text: {len(current_text)} chars, {final_tokens} tokens", file=sys.stderr)
        print(
            f"Total reduction: {original_tokens - final_tokens} tokens "
            f"({(1 - final_tokens/original_tokens) * 100:.1f}%)",
            file=sys.stderr,
        )

        return current_text

    def analyze_text(self, text):
        """Analyze text to show potential optimizations"""
        print("Analyzing text for optimization potential...", file=sys.stderr)

        # Run token-aware analyzer
        cmd = [
            sys.executable,
            str(self.scripts_dir / "03_token_aware.py"),
            "-a",  # analyze mode
            "-m",
            self.config["tokenizer"]["model"],
        ]

        result = subprocess.run(cmd, input=text, capture_output=True, text=True)

        if result.returncode == 0:
            import json

            optimizations = json.loads(result.stdout)

            if optimizations:
                print("\nPotential token-aware optimizations:", file=sys.stderr)
                total_savings = sum(opt["total_savings"] for opt in optimizations[:10])
                for opt in optimizations[:10]:  # Top 10
                    print(
                        f"  '{opt['phrase']}' → '{opt['suggested']}': "
                        f"{opt['occurrences']}x, save {opt['total_savings']} tokens",
                        file=sys.stderr,
                    )
                print(
                    f"\nTotal potential savings from top 10: {total_savings} tokens",
                    file=sys.stderr,
                )
            else:
                print("No significant token optimizations found.", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Token optimization pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a file
  python pipeline.py input.txt -o output.txt
  
  # Process from stdin
  echo "This is a test" | python pipeline.py
  
  # Process with detailed visual output
  python pipeline.py input.txt --verbose
  
  # Analyze without processing
  python pipeline.py input.txt --analyze
  
  # Show token counts only
  python pipeline.py input.txt --count-only
        """,
    )

    parser.add_argument("input", nargs="?", help="Input file (reads from stdin if not provided)")
    parser.add_argument("-o", "--output", help="Output file (prints to stdout if not provided)")
    parser.add_argument(
        "-c", "--config", default="config/pipeline_config.yaml", help="Pipeline configuration file"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed diffs and statistics (requires rich)",
    )
    parser.add_argument(
        "-a",
        "--analyze",
        action="store_true",
        help="Analyze optimization potential without processing",
    )
    parser.add_argument(
        "--count-only", action="store_true", help="Only show token count, don't process"
    )
    parser.add_argument(
        "--stages",
        nargs="+",
        choices=["spell_check", "abbreviations", "token_aware", "ml_paraphrase"],
        help="Run only specific stages",
    )

    args = parser.parse_args()

    # Read input
    if args.input:
        with open(args.input, "r") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    # Use verbose pipeline if requested and available
    if args.verbose and VERBOSE_AVAILABLE:
        from pipeline_verbose import main as verbose_main

        # Re-inject the args
        sys.argv = [sys.argv[0]] + [arg for arg in sys.argv[1:]]
        verbose_main()
        return
    elif args.verbose and not VERBOSE_AVAILABLE:
        print(
            "Warning: Verbose mode requires 'rich' library. Install with: pip install rich",
            file=sys.stderr,
        )
        print("Falling back to standard mode...\n", file=sys.stderr)

    # Initialize pipeline
    pipeline = TokenOptimizationPipeline(config_path=args.config)

    # Handle different modes
    if args.count_only:
        tokens = pipeline.count_tokens(text)
        print(f"{tokens} tokens")

    elif args.analyze:
        pipeline.analyze_text(text)

    else:
        # Run pipeline
        if args.stages:
            # Disable stages not in the list
            for stage in ["spell_check", "abbreviations", "token_aware", "ml_paraphrase"]:
                if stage not in args.stages:
                    pipeline.config["pipeline"][stage]["enabled"] = False

        optimized_text = pipeline.run_pipeline(text)

        # Write output
        if args.output:
            with open(args.output, "w") as f:
                f.write(optimized_text)
        else:
            print(optimized_text)


if __name__ == "__main__":
    main()
