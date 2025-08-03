#!/usr/bin/env python3
"""
Main Pipeline Orchestrator with Verbose Mode
Runs all stages of token optimization with detailed visualization
"""

import sys
import argparse
import subprocess
import tempfile
import yaml
import time
import json
from pathlib import Path
from transformers import AutoTokenizer
from utils.diff_viewer import create_diff_viewer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich import print as rprint


class VerboseTokenOptimizationPipeline:
    def __init__(self, config_path="config/pipeline_config.yaml", verbose=False):
        # Load configuration
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Initialize tokenizer for measurements
        self.tokenizer = AutoTokenizer.from_pretrained(self.config["tokenizer"]["model"])

        # Set up paths
        self.scripts_dir = Path(__file__).parent / "scripts"

        # Verbose mode
        self.verbose = verbose
        self.diff_viewer = create_diff_viewer() if verbose else None
        self.console = Console() if verbose else None

        # Track stages for final summary
        self.stage_history = []

    def count_tokens(self, text):
        """Count tokens in text"""
        return len(self.tokenizer.encode(text, add_special_tokens=False))

    def run_stage(self, stage_name, script_name, input_text, extra_args=None):
        """Run a single pipeline stage with optional verbose output"""
        if not self.config["pipeline"][stage_name]["enabled"]:
            if self.verbose:
                self.console.print(
                    f"[yellow]⏭️  Skipping {stage_name} (disabled in config)[/yellow]"
                )
            else:
                print(f"Skipping {stage_name} (disabled in config)", file=sys.stderr)
            return input_text

        script_path = self.scripts_dir / script_name

        # Prepare command
        cmd = [sys.executable, str(script_path)]
        if extra_args:
            cmd.extend(extra_args)

        # Add verbose flag for stages that support it
        if self.verbose and stage_name in ["abbreviations", "token_aware"]:
            cmd.append("-v")

        # Run the script
        start_time = time.time()

        if self.verbose:
            with self.console.status(
                f"[bold green]Running {stage_name}...[/bold green]", spinner="dots"
            ):
                result = subprocess.run(
                    cmd, input=input_text, capture_output=True, text=True, check=False
                )
        else:
            result = subprocess.run(
                cmd, input=input_text, capture_output=True, text=True, check=False
            )

        elapsed = time.time() - start_time

        if result.returncode != 0:
            if self.verbose:
                self.console.print(f"[red]✗ {stage_name} failed: {result.stderr}[/red]")
            else:
                print(f"✗ {stage_name} failed: {result.stderr}", file=sys.stderr)
            return input_text  # Return original on failure

        output_text = result.stdout

        # Calculate token change
        input_tokens = self.count_tokens(input_text)
        output_tokens = self.count_tokens(output_text)
        tokens_saved = input_tokens - output_tokens

        # Store stage info
        self.stage_history.append((stage_name, output_tokens))

        # Extract stats from stderr if available
        stats = self._extract_stats_from_stderr(result.stderr, stage_name)
        stats["elapsed_time"] = elapsed
        stats["tokens_before"] = input_tokens
        stats["tokens_after"] = output_tokens
        stats["tokens_saved"] = tokens_saved

        if self.verbose:
            # Show stage header
            self.console.print(f"\n[bold cyan]━━━ {stage_name.upper()} ━━━[/bold cyan]")

            # Show diff
            if input_text != output_text:
                self.diff_viewer.show_diff(input_text, output_text, stage_name, stats)
            else:
                self.console.print(f"[yellow]No changes made by {stage_name}[/yellow]")

            # Show performance
            self.console.print(f"[dim]Completed in {elapsed:.3f}s[/dim]\n")
        else:
            print(
                f"✓ {stage_name}: {input_tokens} → {output_tokens} tokens "
                f"(-{tokens_saved}, {elapsed:.2f}s)",
                file=sys.stderr,
            )

        return output_text

    def _extract_stats_from_stderr(self, stderr, stage_name):
        """Extract statistics from stage stderr output"""
        stats = {}

        if not stderr:
            return stats

        # Parse different formats based on stage
        lines = stderr.strip().split("\n")

        if stage_name == "abbreviations":
            # Look for replacement statistics
            replacements = []
            in_replacements = False
            for line in lines:
                if "Top replacements:" in line:
                    in_replacements = True
                    continue
                if in_replacements and line.strip().startswith("'"):
                    # Parse: 'long' → 'short': X times
                    import re

                    match = re.match(r"\s*'(.+)' → '(.*)': (\d+) times", line)
                    if match:
                        replacements.append(
                            {
                                "original": match.group(1),
                                "replacement": match.group(2),
                                "count": int(match.group(3)),
                            }
                        )
            if replacements:
                stats["replacements"] = replacements

        elif stage_name == "token_aware":
            # Look for token optimization stats
            replacements = []
            for line in lines:
                if "'" in line and "→" in line and "saved" in line:
                    # Parse: 'original' → 'replacement': X times, saved Y tokens
                    import re

                    match = re.match(r"\s*'(.+)' → '(.*)': (\d+) times, saved (\d+) tokens", line)
                    if match:
                        replacements.append(
                            {
                                "original": match.group(1),
                                "replacement": match.group(2),
                                "count": int(match.group(3)),
                                "tokens_saved": int(match.group(4)),
                            }
                        )
            if replacements:
                stats["replacements"] = replacements

        return stats

    def run_pipeline(self, input_text):
        """Run the full optimization pipeline with optional verbose output"""
        if self.verbose:
            self.console.print(
                Panel.fit(
                    f"[bold green]Token Optimization Pipeline[/bold green]\n"
                    f"Model: [cyan]{self.config['tokenizer']['model']}[/cyan]",
                    border_style="green",
                )
            )
        else:
            print("Starting token optimization pipeline...", file=sys.stderr)

        original_tokens = self.count_tokens(input_text)
        self.stage_history = [("Original", original_tokens)]

        if self.verbose:
            self.console.print(
                f"\n📝 Original text: [bold]{len(input_text)}[/bold] chars, "
                f"[bold]{original_tokens}[/bold] tokens"
            )
        else:
            print(
                f"Original text: {len(input_text)} chars, {original_tokens} tokens", file=sys.stderr
            )
            print("-" * 50, file=sys.stderr)

        current_text = input_text
        total_start_time = time.time()

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
        total_time = time.time() - total_start_time
        final_tokens = self.count_tokens(current_text)
        total_reduction = original_tokens - final_tokens
        reduction_pct = (total_reduction / original_tokens * 100) if original_tokens > 0 else 0

        if self.verbose:
            # Show comprehensive summary
            self.console.print(f"\n[bold green]━━━ FINAL SUMMARY ━━━[/bold green]")
            self.diff_viewer.show_token_analysis(
                original_tokens, final_tokens, self.stage_history, total_time
            )

            # Show final comparison
            self.console.print(f"\n[bold]Final Comparison:[/bold]")
            self.diff_viewer.show_diff(input_text, current_text, "Complete Pipeline")

            # Cost estimation (rough)
            cost_per_1k_tokens = 0.03  # Example rate
            cost_saved = (total_reduction / 1000) * cost_per_1k_tokens
            self.console.print(
                Panel(
                    f"💰 Estimated cost savings: [green]${cost_saved:.4f}[/green] per request\n"
                    f"📊 Token reduction: [green]{reduction_pct:.1f}%[/green]\n"
                    f"⚡ Processing time: [cyan]{total_time:.2f}s[/cyan]",
                    title="Cost Analysis",
                    border_style="green",
                )
            )
        else:
            print("-" * 50, file=sys.stderr)
            print(f"Final text: {len(current_text)} chars, {final_tokens} tokens", file=sys.stderr)
            print(
                f"Total reduction: {total_reduction} tokens ({reduction_pct:.1f}%)", file=sys.stderr
            )

        return current_text

    def analyze_text(self, text):
        """Analyze text to show potential optimizations"""
        if self.verbose:
            self.console.print(
                Panel.fit(
                    "[bold yellow]Optimization Potential Analysis[/bold yellow]",
                    border_style="yellow",
                )
            )
        else:
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
            optimizations = json.loads(result.stdout)

            if self.verbose and optimizations:
                self.diff_viewer.show_replacements(optimizations, "Potential Optimizations")
            elif optimizations:
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
                msg = "No significant token optimizations found."
                if self.verbose:
                    self.console.print(f"[yellow]{msg}[/yellow]")
                else:
                    print(msg, file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Token optimization pipeline with verbose mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process with detailed output
  python pipeline_verbose.py input.txt -o output.txt --verbose
  
  # See beautiful diffs
  echo "This is a test" | python pipeline_verbose.py --verbose
  
  # Analyze with visual output
  python pipeline_verbose.py input.txt --analyze --verbose
        """,
    )

    parser.add_argument("input", nargs="?", help="Input file (reads from stdin if not provided)")
    parser.add_argument("-o", "--output", help="Output file (prints to stdout if not provided)")
    parser.add_argument(
        "-c", "--config", default="config/pipeline_config.yaml", help="Pipeline configuration file"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed diffs and statistics"
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

    # Initialize pipeline
    pipeline = VerboseTokenOptimizationPipeline(config_path=args.config, verbose=args.verbose)

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
            if not args.verbose:  # Only print result if not in verbose mode
                print(optimized_text)


if __name__ == "__main__":
    main()
