# Technical Implementation Recommendations

## Executive Summary

This document provides concrete technical recommendations for building the Emoji Kitchen CLI tool, including architecture decisions, library choices, project structure, and implementation phases.

---

## Architecture Overview

### High-Level Components

```
┌─────────────────────────────────────────────────────────┐
│                       CLI Interface                       │
│  (argparse - input parsing, help, validation)            │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│                  Orchestrator Layer                       │
│  (download coordination, mode selection, reporting)      │
└───────┬─────────────────────────┬───────────────────────┘
        │                         │
        ▼                         ▼
┌─────────────────┐       ┌──────────────────────┐
│  API Client     │       │  Storage Manager     │
│  (httpx async)  │       │  (file operations)   │
└─────────────────┘       └──────────────────────┘
        │                         │
        ▼                         ▼
┌─────────────────┐       ┌──────────────────────┐
│ Metadata Cache  │       │   Filesystem         │
│ (JSON parser)   │       │   (organized dirs)   │
└─────────────────┘       └──────────────────────┘
```

### Design Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Async-First**: Use async/await throughout for performance
3. **Testability**: Pure functions, dependency injection, clear interfaces
4. **Error Handling**: Graceful degradation, detailed error messages
5. **User Experience**: Progress bars, informative output, fast responses

---

## Technology Stack

### Core Dependencies

```toml
[project]
name = "emoji-kitchen"
version = "0.1.0"
description = "CLI tool for downloading Google Emoji Kitchen combinations"
requires-python = ">=3.10"

dependencies = [
    "httpx>=0.27.0",          # Modern async HTTP client
    "rich>=13.7.0",           # Progress bars and beautiful output
    "emoji>=2.12.1",          # Emoji detection and utilities
    "click>=8.1.0",           # CLI framework (recommended over argparse)
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",          # Testing framework
    "pytest-asyncio>=0.23.0", # Async test support
    "pytest-cov>=4.1.0",      # Coverage reporting
    "ruff>=0.2.0",            # Linting and formatting
    "mypy>=1.8.0",            # Type checking
]
```

### Why These Libraries?

**httpx over requests**
- Native async/await support
- HTTP/2 for better performance
- Same API for sync and async (easier testing)
- Modern, actively maintained

**rich over print**
- Beautiful progress bars
- Color support
- Table formatting for results
- Better UX with minimal code

**click over argparse**
- Cleaner API for complex CLI apps
- Better help text generation
- Built-in parameter validation
- Decorators for subcommands

**emoji library**
- Emoji detection and validation
- Unicode normalization helpers
- Extensive emoji database

---

## Project Structure

```
emoji-kitchen/
├── pyproject.toml              # UV project config
├── README.md                   # User documentation
├── .gitignore                  # Exclude downloads/, .venv/, __pycache__
│
├── src/
│   └── emoji_kitchen/
│       ├── __init__.py         # Package exports
│       ├── __main__.py         # Entry point (python -m emoji_kitchen)
│       │
│       ├── cli.py              # Click CLI interface
│       ├── orchestrator.py     # Download coordination and mode logic
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   ├── client.py       # Async HTTP client wrapper
│       │   └── metadata.py     # Metadata download and parsing
│       │
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── manager.py      # File organization and I/O
│       │   └── paths.py        # Path generation (emoji vs codepoint)
│       │
│       └── utils/
│           ├── __init__.py
│           ├── emoji_utils.py  # Emoji ↔ codepoint conversion
│           ├── validators.py   # Input validation
│           └── reporting.py    # Result summaries and output
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_cli.py
│   ├── test_api_client.py
│   ├── test_emoji_utils.py
│   └── test_orchestrator.py
│
└── downloads/                  # Default output directory (gitignored)
    └── .gitkeep
```

---

## Implementation Phases

### Phase 1: Foundation (2-3 hours)

**Goal:** Basic working tool with single-pair downloads

**Tasks:**
1. Set up project with UV
   ```bash
   uv init emoji-kitchen
   cd emoji-kitchen
   uv add httpx rich emoji click
   ```

2. Implement `emoji_utils.py`
   - emoji_to_codepoint()
   - codepoint_to_emoji()
   - validate_emoji()

3. Implement basic `client.py`
   - Async HTTP client with httpx
   - download_single() function
   - Error handling for 404s

4. Implement `manager.py`
   - create_output_path()
   - save_image()
   - check_exists()

5. Create minimal CLI in `cli.py`
   - Two positional arguments (emoji1, emoji2)
   - --output flag
   - --verbose flag

6. Wire together in `orchestrator.py`
   - download_pair() function

**Success Criteria:**
```bash
emoji-kitchen 😊 🎉
# Output: Downloaded 😊_🎉.png to downloads/😊/
```

---

### Phase 2: All Modes (3-4 hours)

**Goal:** Support batch, all-combinations, and interactive modes

**Tasks:**
1. Implement metadata handling
   - Download metadata.json
   - Cache locally (~/.emoji-kitchen/metadata.json)
   - Parse and index by emoji

2. Add `metadata.py`
   - fetch_metadata()
   - parse_metadata()
   - find_combinations(emoji)

3. Extend CLI with modes
   - `--all` flag for all combinations
   - `--batch <file>` for batch processing
   - `--interactive` for interactive mode

4. Implement batch processing
   - Parse input file (one pair per line)
   - Async download all pairs

5. Implement all-combinations
   - Query metadata for base emoji
   - Download all matches

6. Implement interactive mode
   - Prompt for emoji inputs
   - Loop until user exits

**Success Criteria:**
```bash
emoji-kitchen 😊 --all
# Downloads all 😊 combinations

emoji-kitchen --batch combos.txt
# Processes file with emoji pairs

emoji-kitchen --interactive
# Enters interactive prompt
```

---

### Phase 3: Polish & Optimization (2-3 hours)

**Goal:** Production-ready with excellent UX

**Tasks:**
1. Add progress bars (rich)
   - Show download progress
   - Display speed (images/sec)

2. Implement rate limiting
   - Semaphore-based concurrency control
   - Configurable delay (--delay flag)

3. Add result reporting
   - Summary statistics
   - Failed downloads list
   - Colorized output with rich

4. Error handling improvements
   - Retry logic with exponential backoff
   - Detailed error messages
   - Graceful degradation

5. Add skip-existing logic
   - Check file existence before download
   - Report skipped files

6. Implement filename format options
   - --filename-format [emoji|codepoint|auto]
   - Platform detection for auto mode

**Success Criteria:**
```bash
emoji-kitchen 😊 --all --delay 150 --verbose

# Output:
Downloading... ━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
✓ Downloaded: 45 combinations
⊘ Skipped (existing): 12 combinations
✗ Failed: 3 combinations

Failed combinations:
  - 😊 + 🦄 (combo not available)
  - 😊 + 🌈 (network error)
```

---

### Phase 4: Testing & Documentation (2-3 hours)

**Goal:** High-quality, maintainable codebase

**Tasks:**
1. Write unit tests
   - emoji_utils.py (100% coverage)
   - validators.py
   - paths.py

2. Write integration tests
   - End-to-end CLI tests
   - Mock API responses
   - Test all modes

3. Add type hints
   - Full typing throughout codebase
   - Mypy validation

4. Documentation
   - Comprehensive README
   - Usage examples
   - API documentation (docstrings)

5. Code quality
   - Ruff formatting and linting
   - Remove any TODOs or FIXMEs

**Success Criteria:**
- 80%+ test coverage
- All mypy checks pass
- Clean ruff output
- README with examples

---

## Module Specifications

### cli.py (Click Interface)

```python
import click
from pathlib import Path
from .orchestrator import EmojiKitchenOrchestrator

@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--output', '-o', type=Path, default='downloads',
              help='Output directory for downloads')
@click.option('--delay', '-d', type=int, default=100,
              help='Delay between requests in milliseconds')
@click.option('--verbose', '-v', is_flag=True,
              help='Verbose output')
@click.option('--filename-format', type=click.Choice(['emoji', 'codepoint', 'auto']),
              default='auto', help='Filename format')
def cli(ctx, output, delay, verbose, filename_format):
    """Emoji Kitchen - Download emoji combinations from Google."""
    ctx.ensure_object(dict)
    ctx.obj['config'] = {
        'output': output,
        'delay': delay,
        'verbose': verbose,
        'filename_format': filename_format
    }

    # If no subcommand, enter interactive mode
    if ctx.invoked_subcommand is None:
        interactive_mode(ctx.obj['config'])

@cli.command()
@click.argument('emoji1')
@click.argument('emoji2')
@click.pass_context
def pair(ctx, emoji1, emoji2):
    """Download a single emoji pair."""
    config = ctx.obj['config']
    orchestrator = EmojiKitchenOrchestrator(**config)
    asyncio.run(orchestrator.download_pair(emoji1, emoji2))

@cli.command()
@click.argument('emoji')
@click.pass_context
def all(ctx, emoji):
    """Download all combinations for an emoji."""
    config = ctx.obj['config']
    orchestrator = EmojiKitchenOrchestrator(**config)
    asyncio.run(orchestrator.download_all(emoji))

@cli.command()
@click.argument('file', type=click.File('r'))
@click.pass_context
def batch(ctx, file):
    """Download emoji pairs from a file (one pair per line)."""
    config = ctx.obj['config']
    pairs = [line.strip().split() for line in file if line.strip()]
    orchestrator = EmojiKitchenOrchestrator(**config)
    asyncio.run(orchestrator.download_batch(pairs))

if __name__ == '__main__':
    cli()
```

---

### emoji_utils.py (Core Utilities)

```python
import unicodedata
from typing import Optional

def emoji_to_codepoint(emoji: str) -> str:
    """Convert emoji to hex codepoint(s)."""
    emoji = normalize_emoji(emoji)
    if len(emoji) == 1:
        return hex(ord(emoji))[2:]
    return '_'.join(hex(ord(c))[2:] for c in emoji)

def codepoint_to_emoji(codepoint: str) -> str:
    """Convert hex codepoint(s) to emoji."""
    if '_' not in codepoint:
        return chr(int(codepoint, 16))
    return ''.join(chr(int(cp, 16)) for cp in codepoint.split('_'))

def normalize_emoji(emoji: str) -> str:
    """Normalize emoji to NFC form."""
    return unicodedata.normalize('NFC', emoji)

def validate_emoji(text: str) -> bool:
    """Check if text is a valid emoji."""
    import emoji as emoji_lib
    return emoji_lib.is_emoji(text)

def emoji_to_gstatic_code(emoji: str) -> str:
    """Convert emoji to Google's u-prefixed codepoint format."""
    return f"u{emoji_to_codepoint(emoji)}"
```

---

### client.py (Async HTTP Client)

```python
import httpx
from pathlib import Path
from typing import Optional, Tuple

class EmojiKitchenClient:
    """Async HTTP client for Emoji Kitchen downloads."""

    def __init__(
        self,
        max_concurrent: int = 50,
        timeout: float = 10.0,
        delay_ms: int = 100
    ):
        self.max_concurrent = max_concurrent
        self.timeout = httpx.Timeout(timeout, connect=5.0)
        self.delay_ms = delay_ms
        self.limits = httpx.Limits(
            max_connections=max_concurrent,
            max_keepalive_connections=20
        )

    async def download_image(
        self,
        emoji1: str,
        emoji2: str,
        size: int = 512
    ) -> Tuple[bytes, bool]:
        """Download single emoji combination image."""
        url = self._build_url(emoji1, emoji2, size)

        async with httpx.AsyncClient(
            limits=self.limits,
            timeout=self.timeout
        ) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return (response.content, True)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return (b'', False)
                raise
            except httpx.RequestError:
                return (b'', False)

    def _build_url(self, emoji1: str, emoji2: str, size: int) -> str:
        """Build API URL for emoji pair."""
        return f"https://emojik.vercel.app/s/{emoji1}_{emoji2}?size={size}"
```

---

### orchestrator.py (Coordination Logic)

```python
import asyncio
from pathlib import Path
from typing import List, Tuple
from rich.progress import Progress
from .api.client import EmojiKitchenClient
from .storage.manager import StorageManager
from .utils.reporting import Reporter

class EmojiKitchenOrchestrator:
    """Coordinates downloads across different modes."""

    def __init__(
        self,
        output: Path,
        delay: int = 100,
        verbose: bool = False,
        filename_format: str = 'auto'
    ):
        self.client = EmojiKitchenClient(delay_ms=delay)
        self.storage = StorageManager(output, filename_format)
        self.reporter = Reporter(verbose)

    async def download_pair(self, emoji1: str, emoji2: str):
        """Download single emoji pair."""
        # Check if exists
        if self.storage.exists(emoji1, emoji2):
            self.reporter.log(f"Skipping {emoji1}_{emoji2} (already exists)")
            return

        # Download
        content, success = await self.client.download_image(emoji1, emoji2)

        if success:
            self.storage.save(emoji1, emoji2, content)
            self.reporter.success(f"Downloaded {emoji1}_{emoji2}")
        else:
            self.reporter.error(f"Failed {emoji1}_{emoji2}")

    async def download_batch(self, pairs: List[Tuple[str, str]]):
        """Download multiple pairs with progress tracking."""
        tasks = [self.download_pair(e1, e2) for e1, e2 in pairs]

        with Progress() as progress:
            task = progress.add_task("Downloading...", total=len(tasks))

            for coro in asyncio.as_completed(tasks):
                await coro
                progress.update(task, advance=1)

        self.reporter.summary()
```

---

## Configuration Management

### Environment Variables

```python
# .env support (optional)
import os

EMOJI_KITCHEN_CONFIG = {
    'output_dir': os.getenv('EMOJI_KITCHEN_OUTPUT', 'downloads'),
    'max_concurrent': int(os.getenv('EMOJI_KITCHEN_CONCURRENCY', '50')),
    'delay_ms': int(os.getenv('EMOJI_KITCHEN_DELAY', '100')),
    'cache_dir': os.getenv('EMOJI_KITCHEN_CACHE', '~/.emoji-kitchen'),
}
```

### Config File (Future)

```toml
# ~/.emoji-kitchen/config.toml
[download]
output_dir = "downloads"
max_concurrent = 50
delay_ms = 100
filename_format = "auto"

[cache]
enabled = true
directory = "~/.emoji-kitchen"
ttl_days = 7
```

---

## Error Handling Strategy

### Error Categories

1. **User Input Errors** (Exit code 2)
   - Invalid emoji
   - File not found
   - Invalid arguments

2. **Network Errors** (Retry, then exit code 1)
   - Connection timeout
   - DNS resolution failure
   - Server errors (5xx)

3. **Combination Not Found** (Log, continue)
   - 404 from API
   - Not in metadata

4. **File System Errors** (Exit code 1)
   - Permission denied
   - Disk full
   - Invalid path

### Error Handling Pattern

```python
try:
    result = await download_pair(emoji1, emoji2)
except UserInputError as e:
    console.print(f"[red]Error: {e}[/red]")
    sys.exit(2)
except NetworkError as e:
    console.print(f"[yellow]Network error: {e}. Retrying...[/yellow]")
    # Retry logic
except FileSystemError as e:
    console.print(f"[red]File system error: {e}[/red]")
    sys.exit(1)
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_emoji_utils.py
def test_emoji_to_codepoint():
    assert emoji_to_codepoint("😀") == "1f600"
    assert emoji_to_codepoint("❤️") == "2764_fe0f"

def test_codepoint_to_emoji():
    assert codepoint_to_emoji("1f600") == "😀"

# tests/test_validators.py
def test_validate_emoji():
    assert validate_emoji("😀") is True
    assert validate_emoji("abc") is False
```

### Integration Tests

```python
# tests/test_cli.py
from click.testing import CliRunner

def test_cli_pair_download():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['pair', '😊', '🎉'])
        assert result.exit_code == 0
        assert Path('downloads/😊/😊_🎉.png').exists()
```

---

## Performance Targets

- **Single download**: < 1 second
- **Batch (100 images)**: < 30 seconds
- **All combinations**: < 5 minutes per emoji
- **Memory usage**: < 200 MB
- **CPU usage**: < 50% on single core

---

## Deployment & Distribution

### Installation

```bash
# Development
git clone https://github.com/user/emoji-kitchen
cd emoji-kitchen
uv sync
uv run python -m emoji_kitchen --help

# Production (future)
uv tool install emoji-kitchen
emoji-kitchen --help
```

### Packaging

```toml
[project.scripts]
emoji-kitchen = "emoji_kitchen.cli:cli"
```

---

## Next Steps for Implementation

1. ✅ Review all research documents
2. ⏭ Set up project structure with UV
3. ⏭ Implement Phase 1 (foundation)
4. ⏭ Test single pair downloads
5. ⏭ Implement Phase 2 (all modes)
6. ⏭ Implement Phase 3 (polish)
7. ⏭ Implement Phase 4 (tests & docs)
8. ⏭ Deploy and share

---

*Recommendations completed: 2025-11-19*
*Estimated total implementation time: 10-15 hours*
*Estimated time to working prototype: 2-3 hours*
