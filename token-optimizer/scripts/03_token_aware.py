#!/usr/bin/env python3
"""
Stage 3: Token-Aware Replacements
Replaces phrases based on actual token count savings
"""

import sys
import argparse
from pathlib import Path
from transformers import AutoTokenizer
from collections import defaultdict
import json


class TokenAwareOptimizer:
    def __init__(self, model_name="gpt2", min_savings=1):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.min_savings = min_savings

        # Common replacements to test
        self.replacement_candidates = {
            # Contractions
            "it is": "it's",
            "you are": "you're",
            "we are": "we're",
            "they are": "they're",
            "i am": "i'm",
            "do not": "don't",
            "does not": "doesn't",
            "did not": "didn't",
            "will not": "won't",
            "can not": "can't",
            "cannot": "can't",
            "should not": "shouldn't",
            "would not": "wouldn't",
            "could not": "couldn't",
            "have not": "haven't",
            "has not": "hasn't",
            "had not": "hadn't",
            # Common reductions
            "going to": "gonna",
            "want to": "wanna",
            "got to": "gotta",
            # Formal to informal
            "approximately": "~",
            "equals": "=",
            "greater than": ">",
            "less than": "<",
            "and/or": "or",
            # Technical shortcuts
            "version": "v",
            "versus": "vs",
            "example": "e.g.",
            "that is": "i.e.",
            "et cetera": "etc",
            "number": "#",
            # Remove filler words (context dependent)
            "basically": "",
            "actually": "",
            "really": "",
            "very": "",
            "just": "",
            "quite": "",
            "rather": "",
        }

        # Build token-efficient map
        self.token_efficient_map = self._build_efficient_map()

    def _count_tokens(self, text):
        """Count tokens for a given text"""
        return len(self.tokenizer.encode(text, add_special_tokens=False))

    def _build_efficient_map(self):
        """Build map of replacements that actually save tokens"""
        efficient_map = {}

        for original, replacement in self.replacement_candidates.items():
            orig_tokens = self._count_tokens(original)
            repl_tokens = self._count_tokens(replacement) if replacement else 0

            savings = orig_tokens - repl_tokens
            if savings >= self.min_savings:
                efficient_map[original] = {
                    "replacement": replacement,
                    "savings": savings,
                    "original_tokens": orig_tokens,
                    "replacement_tokens": repl_tokens,
                }

        return efficient_map

    def optimize_text(self, text):
        """Optimize text based on token counts"""
        import re

        optimized_text = text
        total_savings = 0
        replacements_made = []

        # Sort by potential savings (highest first)
        sorted_replacements = sorted(
            self.token_efficient_map.items(), key=lambda x: x[1]["savings"], reverse=True
        )

        for original, info in sorted_replacements:
            replacement = info["replacement"]

            # Create pattern for case-insensitive whole word matching
            pattern = re.compile(r"\b" + re.escape(original) + r"\b", re.IGNORECASE)

            # Check if pattern exists in text
            matches = pattern.findall(optimized_text)
            if matches:
                # Calculate actual token savings in context
                sample_match = matches[0]
                before_sample = pattern.sub(replacement, sample_match)

                # Verify token savings in actual context
                context_original_tokens = self._count_tokens(sample_match)
                context_replacement_tokens = self._count_tokens(before_sample)
                actual_savings = context_original_tokens - context_replacement_tokens

                if actual_savings >= self.min_savings:
                    # Perform replacement
                    def replace_func(match):
                        matched_text = match.group()
                        # Handle empty replacements
                        if not replacement:
                            return ""
                        # Preserve case for non-empty replacements
                        if matched_text.isupper() and len(replacement) > 1:
                            return replacement.upper()
                        elif matched_text[0].isupper() and len(replacement) > 1:
                            return replacement[0].upper() + replacement[1:]
                        return replacement

                    optimized_text = pattern.sub(replace_func, optimized_text)

                    replacements_made.append(
                        {
                            "original": original,
                            "replacement": replacement,
                            "count": len(matches),
                            "tokens_saved": actual_savings * len(matches),
                        }
                    )
                    total_savings += actual_savings * len(matches)

        # Clean up extra spaces
        optimized_text = re.sub(r"\s+", " ", optimized_text)
        optimized_text = re.sub(r"\s+([,.!?;:])", r"\1", optimized_text)

        return optimized_text.strip(), {
            "total_tokens_saved": total_savings,
            "replacements": replacements_made,
            "original_tokens": self._count_tokens(text),
            "optimized_tokens": self._count_tokens(optimized_text),
        }

    def analyze_text(self, text):
        """Analyze text for potential optimizations without applying them"""
        potential_optimizations = []

        for original, info in self.token_efficient_map.items():
            import re

            pattern = re.compile(r"\b" + re.escape(original) + r"\b", re.IGNORECASE)
            matches = pattern.findall(text)

            if matches:
                potential_optimizations.append(
                    {
                        "phrase": original,
                        "suggested": info["replacement"],
                        "occurrences": len(matches),
                        "tokens_per_occurrence": info["savings"],
                        "total_savings": info["savings"] * len(matches),
                    }
                )

        # Sort by total potential savings
        potential_optimizations.sort(key=lambda x: x["total_savings"], reverse=True)

        return potential_optimizations


def main():
    parser = argparse.ArgumentParser(description="Token-aware text optimizer")
    parser.add_argument("input", nargs="?", help="Input file or - for stdin")
    parser.add_argument("-o", "--output", help="Output file or - for stdout")
    parser.add_argument(
        "-m", "--model", default="gpt2", help="Tokenizer model name (default: gpt2)"
    )
    parser.add_argument(
        "-s",
        "--min-savings",
        type=int,
        default=1,
        help="Minimum token savings required (default: 1)",
    )
    parser.add_argument("-a", "--analyze", action="store_true", help="Analyze only, don't optimize")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show optimization statistics")

    args = parser.parse_args()

    # Read input
    if args.input and args.input != "-":
        with open(args.input, "r") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    # Initialize optimizer
    print(f"Loading tokenizer: {args.model}...", file=sys.stderr)
    optimizer = TokenAwareOptimizer(model_name=args.model, min_savings=args.min_savings)

    if args.analyze:
        # Analysis mode
        optimizations = optimizer.analyze_text(text)
        print(json.dumps(optimizations, indent=2))
    else:
        # Optimization mode
        optimized_text, stats = optimizer.optimize_text(text)

        # Write output
        if args.output and args.output != "-":
            with open(args.output, "w") as f:
                f.write(optimized_text)
        else:
            print(optimized_text)

        # Show statistics if verbose
        if args.verbose:
            print("\n--- Token Optimization Statistics ---", file=sys.stderr)
            print(f"Original tokens: {stats['original_tokens']}", file=sys.stderr)
            print(f"Optimized tokens: {stats['optimized_tokens']}", file=sys.stderr)
            print(f"Total tokens saved: {stats['total_tokens_saved']}", file=sys.stderr)
            print(
                f"Reduction: {(stats['total_tokens_saved'] / stats['original_tokens'] * 100):.1f}%",
                file=sys.stderr,
            )

            if stats["replacements"]:
                print("\nReplacements made:", file=sys.stderr)
                for repl in stats["replacements"]:
                    print(
                        f"  '{repl['original']}' → '{repl['replacement']}': "
                        f"{repl['count']} times, saved {repl['tokens_saved']} tokens",
                        file=sys.stderr,
                    )


if __name__ == "__main__":
    main()
