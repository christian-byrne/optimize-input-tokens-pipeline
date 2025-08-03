#!/usr/bin/env python3
"""
Stage 1: Spell Checking
Corrects typos and common misspellings to reduce token count
"""

import sys
import json
import argparse
from pathlib import Path
from symspellpy import SymSpell, Verbosity
import pkg_resources


class SpellChecker:
    def __init__(self, max_edit_distance=2):
        self.sym_spell = SymSpell(max_edit_distance=max_edit_distance, prefix_length=7)

        # Load frequency dictionary
        dictionary_path = pkg_resources.resource_filename(
            "symspellpy", "frequency_dictionary_en_82_765.txt"
        )
        self.sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)

    def correct_text(self, text):
        """Correct spelling mistakes while preserving code/URLs"""
        lines = text.split("\n")
        corrected_lines = []

        for line in lines:
            # Skip code blocks
            if line.strip().startswith("```") or line.strip().startswith("    "):
                corrected_lines.append(line)
                continue

            words = line.split()
            corrected_words = []

            for word in words:
                # Skip URLs, paths, and code-like strings
                if any(
                    char in word
                    for char in ["/", "\\", ".com", ".org", "@", "$", "{", "}", "[", "]", "http"]
                ):
                    corrected_words.append(word)
                    continue

                # Handle punctuation
                prefix = ""
                suffix = ""
                clean_word = word

                # Extract leading/trailing punctuation
                while clean_word and not clean_word[0].isalnum():
                    prefix += clean_word[0]
                    clean_word = clean_word[1:]
                while clean_word and not clean_word[-1].isalnum():
                    suffix = clean_word[-1] + suffix
                    clean_word = clean_word[:-1]

                if not clean_word:
                    corrected_words.append(word)
                    continue

                # Get spelling correction
                suggestions = self.sym_spell.lookup(
                    clean_word.lower(), Verbosity.CLOSEST, max_edit_distance=2
                )

                if suggestions and suggestions[0].distance <= 1:
                    # Preserve original case
                    corrected = suggestions[0].term
                    if clean_word.isupper():
                        corrected = corrected.upper()
                    elif clean_word[0].isupper():
                        corrected = corrected.capitalize()

                    corrected_words.append(prefix + corrected + suffix)
                else:
                    corrected_words.append(word)

            corrected_lines.append(" ".join(corrected_words))

        return "\n".join(corrected_lines)


def main():
    parser = argparse.ArgumentParser(description="Spell checker for token optimization")
    parser.add_argument("input", nargs="?", help="Input file or - for stdin")
    parser.add_argument("-o", "--output", help="Output file or - for stdout")
    parser.add_argument(
        "-d", "--max-distance", type=int, default=2, help="Maximum edit distance for corrections"
    )

    args = parser.parse_args()

    # Read input
    if args.input and args.input != "-":
        with open(args.input, "r") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    # Process
    checker = SpellChecker(max_edit_distance=args.max_distance)
    corrected_text = checker.correct_text(text)

    # Write output
    if args.output and args.output != "-":
        with open(args.output, "w") as f:
            f.write(corrected_text)
    else:
        print(corrected_text)


if __name__ == "__main__":
    main()
