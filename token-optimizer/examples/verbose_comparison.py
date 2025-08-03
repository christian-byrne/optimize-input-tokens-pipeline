#!/usr/bin/env python3
"""
Example showing the difference between normal and verbose mode
"""

import subprocess
import sys

# Sample text with many optimization opportunities
sample_text = """
I would like to request your assistance with understanding the repository structure.
Could you please provide information about the development environment configuration?
It is important to note that we have multiple environments: development, production.
The authentication and authorization requirements need to be documented.
Thank you very much for your help with this request.
"""

print("🔤 Original Text:")
print("-" * 50)
print(sample_text)
print("-" * 50)

print("\n📊 Running in NORMAL mode:")
print("=" * 50)
result = subprocess.run(
    [sys.executable, "pipeline.py"], input=sample_text, capture_output=True, text=True
)
print("Output:", result.stdout)
print("Stats:", result.stderr)

print("\n🎨 Running in VERBOSE mode:")
print("=" * 50)
print("(This would show colorful diffs, tables, and progress bars)")
print("Run: echo 'your text' | python pipeline.py --verbose")
print("\nFeatures in verbose mode:")
print("✓ Side-by-side diffs with color highlighting")
print("✓ Token count visualization with progress bars")
print("✓ Detailed replacement statistics in tables")
print("✓ Stage-by-stage transformations")
print("✓ Performance metrics and cost analysis")
print("✓ Beautiful terminal UI with Rich library")
