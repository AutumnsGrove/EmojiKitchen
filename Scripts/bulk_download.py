#!/usr/bin/env python3
"""
Bulk download script for all emoji combinations from top 100 emojis.

This script programmatically generates all possible combinations (100 x 100 = 10,000)
and downloads them in parallel with optimized concurrency.
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import List, Tuple
from itertools import product

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.emoji_kitchen.api.client import EmojiKitchenClient
from src.emoji_kitchen.storage.manager import StorageManager
from src.emoji_kitchen.utils.emoji_utils import emoji_to_codepoint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.panel import Panel

console = Console()

# Top 100 most commonly used emojis
# Organized by category for clarity
TOP_100_EMOJIS = [
    # Smileys & Emotion (25)
    "😀", "😃", "😄", "😁", "😆", "😅", "🤣", "😂", "🙂", "🙃",
    "😉", "😊", "😇", "🥰", "😍", "🤩", "😘", "😗", "😚", "😙",
    "🥲", "😋", "😛", "😜", "🤪",

    # More Smileys & Negative Emotions (15)
    "😝", "🤑", "🤗", "🤭", "🤫", "🤔", "🤐", "🤨", "😐", "😑",
    "😶", "😏", "😒", "🙄", "😬",

    # Sad/Worried/Sick (15)
    "😮", "🤯", "😳", "🥺", "😢", "😭", "😤", "😠", "😡", "🤬",
    "😈", "👿", "💀", "☠️", "💩",

    # Hearts & Love (10)
    "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔",

    # Hands & Gestures (15)
    "👍", "👎", "👊", "✊", "🤛", "🤜", "👏", "🙌", "👐", "🤲",
    "🤝", "🙏", "✌️", "🤞", "🤟",

    # Animals (10)
    "🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐨", "🐯",

    # Food & Drink (5)
    "🍎", "🍕", "🍔", "🌮", "🍦",

    # Nature & Weather (5)
    "🌈", "⭐", "🌙", "☀️", "🔥",
]

# Ensure exactly 100 emojis
assert len(TOP_100_EMOJIS) == 100, f"Expected 100 emojis, got {len(TOP_100_EMOJIS)}"


class BulkDownloader:
    """Optimized bulk downloader for emoji combinations."""

    def __init__(
        self,
        output_dir: Path,
        size: int = 100,
        max_concurrent: int = 100,
        delay_ms: int = 50
    ):
        """
        Initialize bulk downloader.

        Args:
            output_dir: Directory for downloaded files
            size: Image size in pixels
            max_concurrent: Maximum concurrent downloads
            delay_ms: Rate limiting delay in milliseconds
        """
        self.output_dir = Path(output_dir)
        self.size = size
        self.max_concurrent = max_concurrent
        self.delay_ms = delay_ms

        self.storage = StorageManager(output_dir, filename_format='emoji')

        # Statistics
        self.successes = 0
        self.failures = 0
        self.skipped = 0
        self.not_found = 0

        # Track failures for reporting
        self.failed_pairs: List[Tuple[str, str, str]] = []  # (emoji1, emoji2, error)

    def generate_all_combinations(self, emojis: List[str]) -> List[Tuple[str, str]]:
        """
        Generate all possible emoji combinations.

        Args:
            emojis: List of emojis

        Returns:
            List of (emoji1, emoji2) tuples
        """
        # Generate all combinations including same emoji with itself
        return list(product(emojis, repeat=2))

    async def download_batch_chunk(
        self,
        client: EmojiKitchenClient,
        pairs: List[Tuple[str, str]],
        progress: Progress,
        task_id
    ):
        """
        Download a chunk of emoji pairs concurrently.

        Args:
            client: HTTP client
            pairs: List of emoji pairs to download
            progress: Rich progress bar
            task_id: Progress task ID
        """
        # Process each pair
        for emoji1, emoji2 in pairs:
            # Check if already exists
            if self.storage.file_exists(emoji1, emoji2):
                self.skipped += 1
                progress.update(task_id, advance=1)
                continue

            # Download
            success, content, error, status_code = await client.download_image(
                emoji1, emoji2, self.size
            )

            if success and content:
                try:
                    self.storage.save(emoji1, emoji2, content)
                    self.successes += 1
                except Exception as e:
                    self.failures += 1
                    self.failed_pairs.append((emoji1, emoji2, str(e)))
            else:
                if status_code == 404:
                    self.not_found += 1
                else:
                    self.failures += 1
                    self.failed_pairs.append((emoji1, emoji2, error or "Unknown error"))

            progress.update(task_id, advance=1)

    async def download_all(
        self,
        emoji_pairs: List[Tuple[str, str]],
        batch_size: int = 500
    ):
        """
        Download all emoji combinations with progress tracking.

        Args:
            emoji_pairs: List of all emoji pairs to download
            batch_size: Number of pairs per batch
        """
        total = len(emoji_pairs)

        console.print(Panel(
            f"[bold]Downloading {total:,} emoji combinations[/bold]\n"
            f"Size: {self.size}x{self.size}px | Concurrency: {self.max_concurrent}",
            title="Emoji Kitchen Bulk Download",
            border_style="blue"
        ))

        start_time = time.time()

        # Create progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=50),
            TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
            TextColumn("({task.completed}/{task.total})"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console,
            refresh_per_second=10
        ) as progress:

            task_id = progress.add_task("Downloading", total=total)

            async with EmojiKitchenClient(
                delay_ms=self.delay_ms,
                max_concurrent=self.max_concurrent,
                timeout_seconds=15.0,
                max_retries=3
            ) as client:
                # Process in batches for better memory management
                for i in range(0, total, batch_size):
                    batch = emoji_pairs[i:i + batch_size]

                    # Create concurrent tasks for this batch
                    tasks = []
                    for pair in batch:
                        tasks.append(
                            self.process_single(client, pair[0], pair[1], progress, task_id)
                        )

                    # Run batch concurrently
                    await asyncio.gather(*tasks)

        duration = time.time() - start_time

        # Print summary
        self.print_summary(duration)

    async def process_single(
        self,
        client: EmojiKitchenClient,
        emoji1: str,
        emoji2: str,
        progress: Progress,
        task_id
    ):
        """Process a single emoji pair download."""
        # Check if already exists
        if self.storage.file_exists(emoji1, emoji2):
            self.skipped += 1
            progress.update(task_id, advance=1)
            return

        # Download
        success, content, error, status_code = await client.download_image(
            emoji1, emoji2, self.size
        )

        if success and content:
            try:
                self.storage.save(emoji1, emoji2, content)
                self.successes += 1
            except Exception as e:
                self.failures += 1
                self.failed_pairs.append((emoji1, emoji2, str(e)))
        else:
            if status_code == 404:
                self.not_found += 1
            else:
                self.failures += 1
                self.failed_pairs.append((emoji1, emoji2, error or "Unknown error"))

        progress.update(task_id, advance=1)

    def print_summary(self, duration: float):
        """Print download summary."""
        total_attempted = self.successes + self.failures + self.not_found + self.skipped
        rate = total_attempted / duration if duration > 0 else 0

        console.print("\n")
        console.print(Panel(
            f"[green]Successful downloads:[/green] {self.successes:,}\n"
            f"[yellow]Skipped (existing):[/yellow] {self.skipped:,}\n"
            f"[dim]Not found (404):[/dim] {self.not_found:,}\n"
            f"[red]Failed:[/red] {self.failures:,}\n"
            f"\n"
            f"[blue]Total processed:[/blue] {total_attempted:,}\n"
            f"[blue]Duration:[/blue] {duration:.1f}s\n"
            f"[blue]Rate:[/blue] {rate:.1f} combinations/s",
            title="Download Summary",
            border_style="green" if self.failures == 0 else "yellow"
        ))

        # Show some failure details if there are failures
        if self.failed_pairs and len(self.failed_pairs) <= 20:
            console.print("\n[bold red]Failed downloads:[/bold red]")
            for emoji1, emoji2, error in self.failed_pairs[:20]:
                console.print(f"  {emoji1} + {emoji2}: {error}")
        elif self.failed_pairs:
            console.print(f"\n[bold red]First 20 of {len(self.failed_pairs)} failures:[/bold red]")
            for emoji1, emoji2, error in self.failed_pairs[:20]:
                console.print(f"  {emoji1} + {emoji2}: {error}")


async def main():
    """Main entry point for bulk download."""
    console.print("[bold blue]Emoji Kitchen Bulk Downloader[/bold blue]")
    console.print(f"Using {len(TOP_100_EMOJIS)} emojis")

    # Configuration
    output_dir = Path(__file__).parent.parent / "bulk-downloads"
    size = 100  # 100x100 pixels as requested
    max_concurrent = 100  # High concurrency for speed
    delay_ms = 25  # Low delay for speed (API is quite tolerant)

    # Initialize downloader
    downloader = BulkDownloader(
        output_dir=output_dir,
        size=size,
        max_concurrent=max_concurrent,
        delay_ms=delay_ms
    )

    # Generate all combinations
    all_pairs = downloader.generate_all_combinations(TOP_100_EMOJIS)
    console.print(f"Generated {len(all_pairs):,} combinations")

    # Download all
    await downloader.download_all(all_pairs, batch_size=500)

    console.print(f"\n[bold green]Downloads saved to:[/bold green] {output_dir}")


if __name__ == "__main__":
    asyncio.run(main())
