# Performance & Async Download Patterns

## Executive Summary

Downloading 100,000+ emoji combinations requires efficient async patterns, connection pooling, rate limiting, and streaming downloads. This guide provides proven patterns for high-performance HTTP operations in Python.

---

## Performance Baseline

### Emoji Kitchen Image Characteristics

**File Format:** PNG
**Typical Size:** 5-50 KB per image (estimated)
**Total Dataset:** 100,000+ images
**Estimated Total Size:** 500 MB - 5 GB

**Compression:**
- PNG format is already compressed
- No additional compression needed
- Serve images as-is from CDN

### Download Speed Expectations

**Single-threaded (synchronous):**
- ~1-2 images/second
- Total time: 14-28 hours for full dataset

**Multi-threaded (10 workers):**
- ~10-20 images/second
- Total time: 1.5-3 hours for full dataset

**Async (50 concurrent connections):**
- ~50-100 images/second
- Total time: 15-30 minutes for full dataset

**Conclusion:** Async is essential for reasonable performance

---

## Library Comparison

### requests (Synchronous)

**Pros:**
- Simple, well-known API
- Excellent documentation
- Session support for connection pooling

**Cons:**
- Not async - blocks on I/O
- Requires threading/multiprocessing for concurrency
- Higher overhead per request

**Best for:** Quick prototypes, single downloads

---

### httpx (Modern Hybrid)

**Pros:**
- Sync AND async support in one library
- Same API for both modes
- HTTP/2 support
- Built-in timeout handling
- Excellent for gradual migration

**Cons:**
- Slightly less mature than requests
- Smaller community/ecosystem

**Example:**
```python
import httpx

# Sync mode (development/testing)
def download_sync(url: str) -> bytes:
    with httpx.Client() as client:
        response = client.get(url)
        return response.content

# Async mode (production)
async def download_async(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.content
```

**Best for:** Production CLI tool (recommended)

---

### aiohttp (Pure Async)

**Pros:**
- Battle-tested for high concurrency
- Excellent performance
- Mature ecosystem
- Proven at scale (1M+ requests)

**Cons:**
- Async-only (no sync fallback)
- Different API from requests
- Requires full async implementation

**Example:**
```python
import aiohttp

async def download_image(session: aiohttp.ClientSession, url: str) -> bytes:
    async with session.get(url) as response:
        return await response.read()
```

**Best for:** High-performance batch operations

---

## Recommended: httpx with Async

**Why httpx?**
1. Same API for sync and async (easy testing)
2. HTTP/2 support (better performance)
3. Built-in connection pooling
4. Modern, actively maintained
5. Drop-in requests replacement

---

## Async Download Pattern (httpx)

### Basic Implementation

```python
import asyncio
import httpx
from pathlib import Path
from typing import List, Tuple

async def download_single(
    client: httpx.AsyncClient,
    url: str,
    output_path: Path
) -> Tuple[str, bool]:
    """Download single image to file."""
    try:
        response = await client.get(url)
        response.raise_for_status()

        # Stream to file (memory efficient)
        with open(output_path, 'wb') as f:
            f.write(response.content)

        return (url, True)
    except httpx.HTTPError as e:
        return (url, False)

async def download_batch(
    urls: List[str],
    output_dir: Path,
    max_concurrent: int = 50
) -> dict:
    """Download multiple images with concurrency control."""
    # Configure client
    limits = httpx.Limits(
        max_connections=max_concurrent,
        max_keepalive_connections=20
    )
    timeout = httpx.Timeout(10.0, connect=5.0)

    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        # Create tasks
        tasks = []
        for url in urls:
            filename = url.split('/')[-1]
            output_path = output_dir / filename
            tasks.append(download_single(client, url, output_path))

        # Execute with concurrency control
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    success = sum(1 for _, ok in results if ok)
    failed = len(results) - success

    return {
        'total': len(urls),
        'success': success,
        'failed': failed
    }
```

---

## Advanced Pattern: Rate Limiting

### Built-in Rate Limiter

```python
import asyncio
from time import time

class RateLimiter:
    """Token bucket rate limiter for async operations."""

    def __init__(self, rate: int, per: float = 1.0):
        """
        Args:
            rate: Number of requests
            per: Time period in seconds (e.g., 100 requests per 1.0 second)
        """
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time()
        self.lock = asyncio.Lock()

    async def acquire(self):
        """Acquire permission to make a request."""
        async with self.lock:
            current = time()
            time_passed = current - self.last_check
            self.last_check = current
            self.allowance += time_passed * (self.rate / self.per)

            if self.allowance > self.rate:
                self.allowance = self.rate

            if self.allowance < 1.0:
                sleep_time = (1.0 - self.allowance) * (self.per / self.rate)
                await asyncio.sleep(sleep_time)
                self.allowance = 0.0
            else:
                self.allowance -= 1.0

# Usage
limiter = RateLimiter(rate=100, per=1.0)  # 100 requests per second

async def download_with_rate_limit(client, url, path, limiter):
    await limiter.acquire()
    return await download_single(client, url, path)
```

---

## Semaphore-Based Concurrency Control

Simpler alternative to rate limiting:

```python
import asyncio

async def download_batch_with_semaphore(
    urls: List[str],
    output_dir: Path,
    max_concurrent: int = 50,
    delay_ms: int = 100
):
    """Download with semaphore-based concurrency control."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def download_with_sem(url: str, path: Path):
        async with semaphore:
            result = await download_single(client, url, path)
            # Respectful delay between requests
            await asyncio.sleep(delay_ms / 1000.0)
            return result

    async with httpx.AsyncClient() as client:
        tasks = [
            download_with_sem(url, output_dir / url.split('/')[-1])
            for url in urls
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

---

## Streaming Downloads (Large Files)

For future optimization if images are larger:

```python
async def download_stream(
    client: httpx.AsyncClient,
    url: str,
    output_path: Path,
    chunk_size: int = 8192
) -> bool:
    """Stream download to avoid memory issues."""
    try:
        async with client.stream('GET', url) as response:
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                async for chunk in response.aiter_bytes(chunk_size):
                    f.write(chunk)

        return True
    except httpx.HTTPError:
        return False
```

---

## Progress Tracking

### Using rich for Beautiful Progress Bars

```python
from rich.progress import Progress, BarColumn, TimeRemainingColumn

async def download_with_progress(urls: List[str], output_dir: Path):
    """Download with visual progress bar."""

    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeRemainingColumn(),
    ) as progress:

        task = progress.add_task("[cyan]Downloading...", total=len(urls))

        async with httpx.AsyncClient() as client:
            for url in urls:
                filename = url.split('/')[-1]
                path = output_dir / filename
                await download_single(client, url, path)
                progress.update(task, advance=1)
```

---

## Error Handling & Retry Logic

### Exponential Backoff

```python
import asyncio
from typing import Optional

async def download_with_retry(
    client: httpx.AsyncClient,
    url: str,
    output_path: Path,
    max_retries: int = 3
) -> bool:
    """Download with exponential backoff retry."""

    for attempt in range(max_retries):
        try:
            response = await client.get(url)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                f.write(response.content)

            return True

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # Don't retry 404s (combination doesn't exist)
                return False

            # Retry on 5xx errors
            if e.response.status_code >= 500:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                await asyncio.sleep(wait_time)
                continue

            return False

        except httpx.RequestError:
            # Network errors - retry
            wait_time = 2 ** attempt
            await asyncio.sleep(wait_time)
            continue

    return False
```

---

## Complete Example: Production-Ready Downloader

```python
import asyncio
import httpx
from pathlib import Path
from typing import List, Tuple, Dict
from rich.progress import Progress, BarColumn, TimeRemainingColumn
from dataclasses import dataclass

@dataclass
class DownloadResult:
    """Result of download operation."""
    total: int
    success: int
    failed: int
    skipped: int
    failed_urls: List[str]

class EmojiDownloader:
    """Async emoji image downloader with rate limiting and progress tracking."""

    def __init__(
        self,
        max_concurrent: int = 50,
        delay_ms: int = 100,
        timeout_seconds: float = 10.0
    ):
        self.max_concurrent = max_concurrent
        self.delay_ms = delay_ms
        self.timeout = httpx.Timeout(timeout_seconds, connect=5.0)
        self.limits = httpx.Limits(
            max_connections=max_concurrent,
            max_keepalive_connections=20
        )

    async def download(
        self,
        urls: List[str],
        output_dir: Path,
        skip_existing: bool = True
    ) -> DownloadResult:
        """Download all URLs with progress tracking."""

        # Prepare output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Filter existing files
        if skip_existing:
            urls_to_download = [
                url for url in urls
                if not (output_dir / url.split('/')[-1]).exists()
            ]
            skipped = len(urls) - len(urls_to_download)
        else:
            urls_to_download = urls
            skipped = 0

        # Track results
        failed_urls = []
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def download_one(url: str, progress_task) -> bool:
            """Download single URL with rate limiting."""
            async with semaphore:
                filename = url.split('/')[-1]
                output_path = output_dir / filename

                success = await self._download_with_retry(client, url, output_path)

                # Rate limiting delay
                await asyncio.sleep(self.delay_ms / 1000.0)

                # Update progress
                progress.update(progress_task, advance=1)

                if not success:
                    failed_urls.append(url)

                return success

        # Execute downloads with progress bar
        with Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeRemainingColumn(),
        ) as progress:

            task = progress.add_task(
                "[cyan]Downloading...",
                total=len(urls_to_download)
            )

            async with httpx.AsyncClient(
                limits=self.limits,
                timeout=self.timeout
            ) as client:
                results = await asyncio.gather(
                    *[download_one(url, task) for url in urls_to_download],
                    return_exceptions=True
                )

        # Calculate stats
        success = sum(1 for r in results if r is True)
        failed = len(results) - success

        return DownloadResult(
            total=len(urls),
            success=success,
            failed=failed,
            skipped=skipped,
            failed_urls=failed_urls
        )

    async def _download_with_retry(
        self,
        client: httpx.AsyncClient,
        url: str,
        output_path: Path,
        max_retries: int = 3
    ) -> bool:
        """Download with retry logic."""
        for attempt in range(max_retries):
            try:
                response = await client.get(url)
                response.raise_for_status()

                with open(output_path, 'wb') as f:
                    f.write(response.content)

                return True

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return False  # Don't retry 404s

                if e.response.status_code >= 500:
                    await asyncio.sleep(2 ** attempt)
                    continue

                return False

            except httpx.RequestError:
                await asyncio.sleep(2 ** attempt)
                continue

        return False

# Usage
async def main():
    downloader = EmojiDownloader(
        max_concurrent=50,
        delay_ms=100
    )

    urls = [...]  # List of emoji image URLs
    output_dir = Path("downloads/emojis")

    result = await downloader.download(urls, output_dir)

    print(f"✓ Downloaded: {result.success}")
    print(f"⊘ Skipped: {result.skipped}")
    print(f"✗ Failed: {result.failed}")

    if result.failed_urls:
        print("\nFailed URLs:")
        for url in result.failed_urls:
            print(f"  - {url}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Performance Optimization Checklist

- [ ] Use httpx or aiohttp for async support
- [ ] Implement connection pooling (max_connections)
- [ ] Add rate limiting (100-200ms delay or semaphore)
- [ ] Enable HTTP/2 for multiplexing
- [ ] Skip existing files (avoid redundant downloads)
- [ ] Implement retry with exponential backoff
- [ ] Don't retry 404s (invalid combinations)
- [ ] Stream large files to avoid memory issues
- [ ] Use progress bars for user feedback
- [ ] Handle exceptions gracefully
- [ ] Close connections properly (async context managers)
- [ ] Set appropriate timeouts

---

## Benchmarking Recommendations

### Test Scenarios

1. **Small batch (10 images)**
   - Measure baseline performance
   - Test error handling

2. **Medium batch (100 images)**
   - Test rate limiting behavior
   - Validate progress tracking

3. **Large batch (1000+ images)**
   - Measure sustained throughput
   - Monitor memory usage
   - Test skip-existing logic

### Metrics to Track

- Images per second
- Total time
- Memory usage
- Network bandwidth
- Success/failure rates
- Average file size

---

## Recommended Configuration

```python
# Production settings
EMOJI_DOWNLOADER_CONFIG = {
    'max_concurrent': 50,       # Concurrent downloads
    'delay_ms': 100,            # 100ms between requests = 10 req/sec per worker
    'timeout_seconds': 10.0,    # Total request timeout
    'connect_timeout': 5.0,     # Connection timeout
    'max_retries': 3,           # Retry attempts
    'chunk_size': 8192,         # Streaming chunk size
}

# Conservative settings (respectful)
CONSERVATIVE_CONFIG = {
    'max_concurrent': 20,
    'delay_ms': 200,
    'timeout_seconds': 15.0,
    'connect_timeout': 5.0,
    'max_retries': 3,
    'chunk_size': 8192,
}

# Aggressive settings (fast)
AGGRESSIVE_CONFIG = {
    'max_concurrent': 100,
    'delay_ms': 50,
    'timeout_seconds': 10.0,
    'connect_timeout': 3.0,
    'max_retries': 2,
    'chunk_size': 16384,
}
```

---

## Dependencies

```toml
[project.dependencies]
httpx = "^0.27.0"        # Modern async HTTP client
rich = "^13.7.0"         # Progress bars and formatting
```

Optional:
```toml
aiohttp = "^3.9.0"       # Alternative async HTTP client
aiofiles = "^23.2.0"     # Async file I/O (for very large files)
```

---

## Next Steps

1. Implement basic sync version with requests (prototype)
2. Migrate to httpx async implementation
3. Add rate limiting with semaphore
4. Implement progress bars with rich
5. Add retry logic with exponential backoff
6. Benchmark on small dataset
7. Tune concurrency and delay parameters
8. Test on full dataset

---

*Research completed: 2025-11-19*
*Recommended library: httpx*
*Expected performance: 50-100 images/second*
*Estimated time for 100k images: 15-30 minutes*
