#!/usr/bin/env python3
"""
Stage 2: Abbreviations
Replaces common long forms with standard abbreviations
"""

import sys
import json
import re
import argparse
from pathlib import Path


class AbbreviationReplacer:
    def __init__(self, config_path="config/abbreviations.json"):
        self.abbreviations = {}
        
        # Load abbreviations from config
        config_file = Path(__file__).parent.parent / config_path
        if config_file.exists():
            with open(config_file, 'r') as f:
                data = json.load(f)
                # Flatten all categories
                for category in data.values():
                    self.abbreviations.update(category)
        else:
            print(f"Warning: Abbreviations file not found at {config_file}", file=sys.stderr)
    
    def replace_abbreviations(self, text):
        """Replace long forms with abbreviations"""
        # Sort by length (longest first) to handle multi-word replacements
        sorted_abbrevs = sorted(self.abbreviations.items(), 
                               key=lambda x: len(x[0]), reverse=True)
        
        # Track replacements for logging
        replacements = []
        
        for long_form, short_form in sorted_abbrevs:
            # Skip empty replacements for single words (only remove in phrases)
            if not short_form and ' ' not in long_form:
                continue
            
            # Create case-insensitive pattern with word boundaries
            # For multi-word phrases, use looser boundaries
            if ' ' in long_form:
                pattern = re.compile(r'\b' + re.escape(long_form) + r'\b', re.IGNORECASE)
            else:
                pattern = re.compile(r'\b' + re.escape(long_form) + r'\b', re.IGNORECASE)
            
            # Find all matches before replacement
            matches = pattern.findall(text)
            
            if matches:
                # Perform replacement
                def replace_func(match):
                    matched_text = match.group()
                    # Preserve case for single words
                    if ' ' not in long_form:
                        if matched_text.isupper():
                            return short_form.upper() if short_form else ''
                        elif matched_text[0].isupper():
                            return short_form.capitalize() if short_form else ''
                    return short_form
                
                text = pattern.sub(replace_func, text)
                replacements.append((long_form, short_form, len(matches)))
        
        # Clean up extra spaces from empty replacements
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)  # Fix punctuation spacing
        
        return text.strip(), replacements
    
    def add_custom_abbreviation(self, long_form, short_form):
        """Add a custom abbreviation at runtime"""
        self.abbreviations[long_form] = short_form


def main():
    parser = argparse.ArgumentParser(description='Abbreviation replacer for token optimization')
    parser.add_argument('input', nargs='?', help='Input file or - for stdin')
    parser.add_argument('-o', '--output', help='Output file or - for stdout')
    parser.add_argument('-c', '--config', default='config/abbreviations.json',
                       help='Path to abbreviations config file')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Show replacement statistics')
    
    args = parser.parse_args()
    
    # Read input
    if args.input and args.input != '-':
        with open(args.input, 'r') as f:
            text = f.read()
    else:
        text = sys.stdin.read()
    
    # Process
    replacer = AbbreviationReplacer(config_path=args.config)
    processed_text, replacements = replacer.replace_abbreviations(text)
    
    # Write output
    if args.output and args.output != '-':
        with open(args.output, 'w') as f:
            f.write(processed_text)
    else:
        print(processed_text)
    
    # Show statistics if verbose
    if args.verbose and replacements:
        print("\n--- Abbreviation Statistics ---", file=sys.stderr)
        total_replacements = sum(count for _, _, count in replacements)
        print(f"Total replacements: {total_replacements}", file=sys.stderr)
        print("\nTop replacements:", file=sys.stderr)
        for long_form, short_form, count in sorted(replacements, key=lambda x: x[2], reverse=True)[:10]:
            print(f"  '{long_form}' → '{short_form}': {count} times", file=sys.stderr)


if __name__ == '__main__':
    main()