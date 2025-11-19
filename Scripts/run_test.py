#!/usr/bin/env python3
"""Direct test runner for emoji downloads."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from emoji_kitchen.orchestrator import DownloadOrchestrator


async def main():
    # Read test file
    test_file = Path('Tests/Data/test_emojis_250.txt')
    emoji_pairs = []

    with open(test_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split()
            if len(parts) >= 2:
                emoji_pairs.append((parts[0], parts[1]))

    print(f"Testing with {len(emoji_pairs)} emoji combinations...")

    # Run orchestrator
    orchestrator = DownloadOrchestrator(
        output_dir=Path('test-results'),
        log_dir=Path('logs'),
        delay_ms=100,
        max_concurrent=50,
        skip_existing=False,
        verbose=False,
        filename_format='auto'
    )

    stats = await orchestrator.download_batch(emoji_pairs, size=512, show_progress=True)

    # Check success rate
    success_rate = (stats.successes / stats.total) * 100 if stats.total > 0 else 0
    print(f"\n{'='*60}")
    print(f"TEST RESULTS:")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Required: ≥75%")
    print(f"Status: {'✓ PASSED' if success_rate >= 75.0 else '✗ FAILED'}")
    print(f"{'='*60}\n")

    return 0 if success_rate >= 75.0 else 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
