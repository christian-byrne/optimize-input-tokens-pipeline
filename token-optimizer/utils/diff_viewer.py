#!/usr/bin/env python3
"""
Beautiful terminal diff viewer for token optimization pipeline
"""

import difflib
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.columns import Columns
from rich.progress import track
import re
from typing import List, Tuple, Dict, Any


class DiffViewer:
    def __init__(self):
        self.console = Console()

    def show_diff(self, text1: str, text2: str, stage_name: str, stats: Dict[str, Any] = None):
        """Show a beautiful side-by-side diff with statistics"""
        # Create the diff
        diff = list(
            difflib.unified_diff(
                text1.splitlines(keepends=True),
                text2.splitlines(keepends=True),
                fromfile=f"Before {stage_name}",
                tofile=f"After {stage_name}",
                n=3,
            )
        )

        if not diff:
            self.console.print(f"[yellow]No changes in {stage_name}[/yellow]")
            return

        # Create a beautiful panel with the diff
        self._show_side_by_side(text1, text2, stage_name)

        # Show statistics if provided
        if stats:
            self._show_stats(stats, stage_name)

    def _show_side_by_side(self, text1: str, text2: str, stage_name: str):
        """Show side-by-side comparison"""
        # Split into words for word-level diff
        words1 = text1.split()
        words2 = text2.split()

        # Get word-level diff
        matcher = difflib.SequenceMatcher(None, words1, words2)

        # Build highlighted versions
        highlighted1 = []
        highlighted2 = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                highlighted1.extend(words1[i1:i2])
                highlighted2.extend(words2[j1:j2])
            elif tag == "delete":
                for word in words1[i1:i2]:
                    highlighted1.append(f"[red strike]{word}[/red strike]")
            elif tag == "insert":
                for word in words2[j1:j2]:
                    highlighted2.append(f"[green]{word}[/green]")
            elif tag == "replace":
                for word in words1[i1:i2]:
                    highlighted1.append(f"[red strike]{word}[/red strike]")
                for word in words2[j1:j2]:
                    highlighted2.append(f"[green]{word}[/green]")

        # Create panels
        before_text = " ".join(highlighted1)
        after_text = " ".join(highlighted2)

        # Create table for side-by-side view
        table = Table(show_header=True, header_style="bold magenta", expand=True)
        table.add_column(f"Before {stage_name}", style="dim", width=50)
        table.add_column(f"After {stage_name}", width=50)

        # Add rows with wrapped text
        table.add_row(
            Panel(before_text, border_style="red"), Panel(after_text, border_style="green")
        )

        self.console.print(table)

    def _show_stats(self, stats: Dict[str, Any], stage_name: str):
        """Show statistics in a nice table"""
        stats_table = Table(
            title=f"{stage_name} Statistics", show_header=True, header_style="bold cyan"
        )
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="magenta")

        for key, value in stats.items():
            # Format the key nicely
            formatted_key = key.replace("_", " ").title()

            # Format the value
            if isinstance(value, float):
                formatted_value = f"{value:.2f}"
            elif isinstance(value, list):
                formatted_value = str(len(value))
            else:
                formatted_value = str(value)

            stats_table.add_row(formatted_key, formatted_value)

        self.console.print(stats_table)
        self.console.print()

    def show_inline_diff(self, text1: str, text2: str, stage_name: str):
        """Show inline diff with color coding"""
        diff = list(difflib.ndiff(text1.splitlines(), text2.splitlines()))

        panel_content = []
        for line in diff:
            if line.startswith("+ "):
                panel_content.append(f"[green]{line}[/green]")
            elif line.startswith("- "):
                panel_content.append(f"[red]{line}[/red]")
            elif line.startswith("? "):
                continue  # Skip hint lines
            else:
                panel_content.append(line)

        self.console.print(
            Panel("\n".join(panel_content), title=f"{stage_name} Changes", border_style="blue")
        )

    def show_token_analysis(
        self,
        original_tokens: int,
        current_tokens: int,
        stage_tokens: List[Tuple[str, int]],
        total_time: float,
    ):
        """Show comprehensive token analysis"""
        # Create a progress-style visualization
        table = Table(title="Token Reduction Progress", show_header=True, header_style="bold green")
        table.add_column("Stage", style="cyan", width=25)
        table.add_column("Tokens", justify="right", width=10)
        table.add_column("Reduction", justify="right", width=15)
        table.add_column("Progress", width=40)

        previous_tokens = original_tokens
        for stage_name, tokens in stage_tokens:
            reduction = previous_tokens - tokens
            reduction_pct = (reduction / previous_tokens * 100) if previous_tokens > 0 else 0

            # Create a progress bar
            bar_length = 30
            filled = int((tokens / original_tokens) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)

            # Color based on reduction
            if reduction > 0:
                reduction_str = f"[green]-{reduction} ({reduction_pct:.1f}%)[/green]"
            elif reduction < 0:
                reduction_str = f"[red]+{abs(reduction)} ({abs(reduction_pct):.1f}%)[/red]"
            else:
                reduction_str = "[yellow]No change[/yellow]"

            table.add_row(
                stage_name,
                str(tokens),
                reduction_str,
                f"[blue]{bar}[/blue] {tokens}/{original_tokens}",
            )

            previous_tokens = tokens

        # Add summary row
        total_reduction = original_tokens - current_tokens
        total_pct = (total_reduction / original_tokens * 100) if original_tokens > 0 else 0

        table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold]{current_tokens}[/bold]",
            f"[bold green]-{total_reduction} ({total_pct:.1f}%)[/bold green]",
            f"[bold]Time: {total_time:.2f}s[/bold]",
            style="bold",
        )

        self.console.print(table)

    def show_replacements(self, replacements: List[Dict[str, Any]], stage_name: str):
        """Show detailed replacement information"""
        if not replacements:
            return

        table = Table(
            title=f"{stage_name} Replacements", show_header=True, header_style="bold yellow"
        )
        table.add_column("Original", style="red")
        table.add_column("Replacement", style="green")
        table.add_column("Count", justify="right")
        table.add_column("Tokens Saved", justify="right")

        # Sort by tokens saved
        sorted_replacements = sorted(
            replacements, key=lambda x: x.get("tokens_saved", 0), reverse=True
        )

        for repl in sorted_replacements[:10]:  # Show top 10
            table.add_row(
                repl.get("original", repl.get("phrase", "")),
                repl.get("replacement", repl.get("suggested", "")),
                str(repl.get("count", repl.get("occurrences", 1))),
                str(repl.get("tokens_saved", repl.get("total_savings", 0))),
            )

        if len(replacements) > 10:
            table.add_row(
                f"[dim]... and {len(replacements) - 10} more[/dim]", "", "", "", style="dim"
            )

        self.console.print(table)


def create_diff_viewer():
    """Factory function to create a diff viewer"""
    return DiffViewer()
