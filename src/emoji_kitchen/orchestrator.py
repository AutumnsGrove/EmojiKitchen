"""Orchestrator for coordinating emoji combination downloads."""

import asyncio
import time
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass

from .api.client import EmojiKitchenClient
from .storage.manager import StorageManager
from .utils.json_logger import JSONLogger
from .utils.reporting import (
    print_summary,
    print_failures,
    create_progress_bar,
    print_info
)


@dataclass
class DownloadStats:
    """Statistics for a download session."""
    total: int = 0
    successes: int = 0
    failures: int = 0
    skipped: int = 0
    duration_seconds: float = 0.0


class DownloadOrchestrator:
    """
    Coordinates emoji combination downloads with progress tracking.

    Features:
    - Async batch downloading
    - Progress bar visualization
    - JSON logging (success/failure tracking)
    - Duplicate detection (skip existing)
    - Summary reporting
    """

    def __init__(
        self,
        output_dir: Path,
        log_dir: Path,
        delay_ms: int = 100,
        max_concurrent: int = 50,
        skip_existing: bool = True,
        verbose: bool = False,
        filename_format: str = 'auto'
    ):
        """
        Initialize download orchestrator.

        Args:
            output_dir: Directory for downloaded files
            log_dir: Directory for log files
            delay_ms: Rate limiting delay in milliseconds
            max_concurrent: Maximum concurrent downloads
            skip_existing: Skip files that already exist
            verbose: Enable verbose logging
            filename_format: Filename format ('emoji', 'codepoint', 'auto')
        """
        self.output_dir = Path(output_dir)
        self.log_dir = Path(log_dir)
        self.delay_ms = delay_ms
        self.max_concurrent = max_concurrent
        self.skip_existing = skip_existing
        self.verbose = verbose

        # Initialize components
        self.storage = StorageManager(output_dir, filename_format=filename_format)
        self.logger = JSONLogger(
            log_dir,
            enable_console=verbose,
            log_level=10 if verbose else 20  # DEBUG if verbose, INFO otherwise
        )

        self.stats = DownloadStats()

    async def download_pair(
        self,
        emoji1: str,
        emoji2: str,
        size: int = 512
    ) -> Tuple[bool, Optional[str]]:
        """
        Download a single emoji pair.

        Args:
            emoji1: First emoji
            emoji2: Second emoji
            size: Image size in pixels

        Returns:
            Tuple of (success, error_message)
        """
        start_time = time.time()

        # Check if already exists
        if self.skip_existing and self.storage.file_exists(emoji1, emoji2):
            self.stats.skipped += 1
            self.logger.info(f"Skipped {emoji1} + {emoji2} (already exists)")
            return True, None

        # Download
        async with EmojiKitchenClient(
            delay_ms=self.delay_ms,
            max_concurrent=self.max_concurrent
        ) as client:
            url = client.build_url(emoji1, emoji2, size)
            success, content, error, status_code = await client.download_image(
                emoji1, emoji2, size
            )

            duration_ms = (time.time() - start_time) * 1000

            if success and content:
                # Save file
                try:
                    file_path = self.storage.save(emoji1, emoji2, content)
                    self.stats.successes += 1

                    # Log success
                    self.logger.log_success(
                        emoji1=emoji1,
                        emoji2=emoji2,
                        file_path=str(file_path),
                        duration_ms=duration_ms,
                        url=url,
                        status_code=status_code
                    )

                    return True, None

                except Exception as e:
                    self.stats.failures += 1
                    error_msg = f"Failed to save file: {str(e)}"

                    self.logger.log_failure(
                        emoji1=emoji1,
                        emoji2=emoji2,
                        error_type="IOError",
                        error_message=error_msg,
                        duration_ms=duration_ms,
                        url=url
                    )

                    return False, error_msg

            else:
                # Download failed
                self.stats.failures += 1

                error_type = "NetworkError"
                if status_code == 404:
                    error_type = "NotFound"
                elif status_code and status_code >= 500:
                    error_type = "ServerError"

                self.logger.log_failure(
                    emoji1=emoji1,
                    emoji2=emoji2,
                    error_type=error_type,
                    error_message=error or "Unknown error",
                    status_code=status_code,
                    duration_ms=duration_ms,
                    url=url
                )

                return False, error

    async def download_batch(
        self,
        emoji_pairs: List[Tuple[str, str]],
        size: int = 512,
        show_progress: bool = True
    ) -> DownloadStats:
        """
        Download multiple emoji combinations.

        Args:
            emoji_pairs: List of (emoji1, emoji2) tuples
            size: Image size in pixels
            show_progress: Show progress bar

        Returns:
            DownloadStats with session statistics
        """
        self.stats = DownloadStats(total=len(emoji_pairs))
        start_time = time.time()

        self.logger.info(f"Starting batch download of {len(emoji_pairs)} combinations")

        if show_progress:
            progress = create_progress_bar(len(emoji_pairs), "Downloading")

            with progress:
                task = progress.add_task("Downloading", total=len(emoji_pairs))

                for emoji1, emoji2 in emoji_pairs:
                    await self.download_pair(emoji1, emoji2, size)
                    progress.update(task, advance=1)
        else:
            # Download without progress bar
            for emoji1, emoji2 in emoji_pairs:
                await self.download_pair(emoji1, emoji2, size)

        self.stats.duration_seconds = time.time() - start_time

        # Print summary
        print_summary(
            total=self.stats.total,
            successes=self.stats.successes,
            failures=self.stats.failures,
            skipped=self.stats.skipped,
            duration_seconds=self.stats.duration_seconds
        )

        # Print failures if any
        if self.logger.failures:
            print_failures(
                [f.to_dict() for f in self.logger.failures],
                limit=20
            )

        # Save logs
        self.logger.close()

        return self.stats

    async def download_single(
        self,
        emoji1: str,
        emoji2: str,
        size: int = 512
    ) -> bool:
        """
        Download a single combination (with reporting).

        Args:
            emoji1: First emoji
            emoji2: Second emoji
            size: Image size in pixels

        Returns:
            True if successful, False otherwise
        """
        success, error = await self.download_pair(emoji1, emoji2, size)

        # Print single result summary
        if self.stats.skipped > 0:
            print_info(f"File already exists, skipped")
        elif success:
            print_info(f"Successfully downloaded to {self.output_dir}")
        else:
            print_info(f"Failed: {error}")

        self.logger.close()

        return success
