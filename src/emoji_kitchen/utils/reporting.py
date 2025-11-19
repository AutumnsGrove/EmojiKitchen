"""Reporting utilities for displaying download results and statistics."""

from typing import Dict, List, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text


console = Console()


def print_summary(
    total: int,
    successes: int,
    failures: int,
    skipped: int = 0,
    duration_seconds: float = 0.0
) -> None:
    """
    Print download summary with statistics.

    Args:
        total: Total attempts
        successes: Successful downloads
        failures: Failed downloads
        skipped: Skipped (already exist)
        duration_seconds: Total duration in seconds
    """
    success_rate = (successes / total * 100) if total > 0 else 0.0

    # Create summary table
    table = Table(title="Download Summary", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan", width=20)
    table.add_column("Count", justify="right", style="green")
    table.add_column("Percentage", justify="right", style="yellow")

    table.add_row("Total Attempts", str(total), "100.0%")
    table.add_row(
        "Successes",
        str(successes),
        f"{success_rate:.1f}%",
        style="bold green"
    )

    if skipped > 0:
        skip_rate = (skipped / total * 100) if total > 0 else 0.0
        table.add_row("Skipped (Exist)", str(skipped), f"{skip_rate:.1f}%", style="blue")

    if failures > 0:
        failure_rate = (failures / total * 100) if total > 0 else 0.0
        table.add_row("Failures", str(failures), f"{failure_rate:.1f}%", style="bold red")

    console.print(table)

    # Performance stats
    if duration_seconds > 0:
        images_per_second = total / duration_seconds
        console.print(f"\n[bold]Performance:[/bold] {images_per_second:.1f} images/second")
        console.print(f"[bold]Duration:[/bold] {duration_seconds:.1f} seconds")


def print_failures(failures: List[Dict[str, Any]], limit: int = 10) -> None:
    """
    Print table of failed downloads.

    Args:
        failures: List of failure dictionaries
        limit: Maximum number of failures to display
    """
    if not failures:
        return

    console.print(f"\n[bold red]Failed Downloads ({len(failures)} total):[/bold red]")

    # Create failures table
    table = Table(show_header=True, header_style="bold red")
    table.add_column("Emoji Pair", style="cyan")
    table.add_column("Error Type", style="yellow")
    table.add_column("Details", style="white")

    for failure in failures[:limit]:
        emoji1 = failure.get('emoji1', '?')
        emoji2 = failure.get('emoji2', '?')
        error_type = failure.get('error_type', 'Unknown')
        error_msg = failure.get('error_message', 'No details')

        # Truncate long error messages
        if len(error_msg) > 50:
            error_msg = error_msg[:47] + "..."

        table.add_row(f"{emoji1} + {emoji2}", error_type, error_msg)

    console.print(table)

    if len(failures) > limit:
        console.print(f"\n[dim]... and {len(failures) - limit} more failures[/dim]")


def print_success_message(emoji1: str, emoji2: str, file_path: str) -> None:
    """Print success message for single download."""
    console.print(f"[green][/green] Downloaded {emoji1} + {emoji2} ’ {file_path}")


def print_error_message(emoji1: str, emoji2: str, error: str) -> None:
    """Print error message for single download."""
    console.print(f"[red][/red] Failed {emoji1} + {emoji2}: {error}")


def print_skip_message(emoji1: str, emoji2: str) -> None:
    """Print skip message for existing file."""
    console.print(f"[blue]™[/blue] Skipped {emoji1} + {emoji2} (already exists)")


def print_header(title: str) -> None:
    """Print styled header."""
    text = Text(title, style="bold magenta")
    console.print(Panel(text, expand=False))


def print_progress_start(total: int, emoji: str = None) -> None:
    """Print message when starting downloads."""
    if emoji:
        console.print(f"\n[bold]Starting download of all combinations for {emoji}...[/bold]")
    else:
        console.print(f"\n[bold]Starting download of {total} combinations...[/bold]")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"[cyan]9[/cyan] {message}")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[yellow] [/yellow] {message}")


def print_error(message: str) -> None:
    """Print error message."""
    console.print(f"[red][/red] {message}")


def create_progress_bar(total: int, description: str = "Downloading"):
    """
    Create Rich progress bar.

    Args:
        total: Total number of items
        description: Description text

    Returns:
        Rich Progress instance
    """
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed}/{task.total})"),
        TimeRemainingColumn(),
        console=console
    )

    return progress
