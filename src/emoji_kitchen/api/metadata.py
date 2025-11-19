"""Metadata handler for Emoji Kitchen (optional - for advanced features)."""

import json
from pathlib import Path
from typing import Optional, List, Tuple
import httpx


class MetadataManager:
    """
    Manages Emoji Kitchen metadata for finding valid combinations.

    Note: This is optional. The Vercel API can be used directly without metadata.
    Metadata is useful for:
    - Finding all combinations for an emoji
    - Validating combinations before download
    - Bulk operations
    """

    METADATA_URL = "https://raw.githubusercontent.com/xsalazar/emoji-kitchen-backend/main/app/metadata.json"

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize metadata manager.

        Args:
            cache_dir: Directory for caching metadata (default: ~/.emoji-kitchen/)
        """
        if cache_dir is None:
            cache_dir = Path.home() / '.emoji-kitchen'

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.cache_file = self.cache_dir / 'metadata.json'
        self.metadata: Optional[dict] = None

    async def download_metadata(self) -> bool:
        """
        Download metadata from GitHub.

        Returns:
            True if successful, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.METADATA_URL, timeout=30.0)
                response.raise_for_status()

                # Save to cache
                self.cache_file.write_bytes(response.content)

                return True

        except Exception as e:
            print(f"Failed to download metadata: {e}")
            return False

    def load_metadata(self) -> bool:
        """
        Load metadata from cache.

        Returns:
            True if successful, False if cache doesn't exist
        """
        if not self.cache_file.exists():
            return False

        try:
            with self.cache_file.open('r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            return True
        except Exception as e:
            print(f"Failed to load metadata: {e}")
            return False

    async def ensure_metadata(self) -> bool:
        """
        Ensure metadata is available (load from cache or download).

        Returns:
            True if metadata is available, False otherwise
        """
        # Try loading from cache first
        if self.load_metadata():
            return True

        # Download if cache doesn't exist
        if await self.download_metadata():
            return self.load_metadata()

        return False

    def find_combinations(self, emoji: str) -> List[Tuple[str, str]]:
        """
        Find all combinations for a given emoji.

        Args:
            emoji: Base emoji

        Returns:
            List of (emoji1, emoji2) tuples

        Note: Returns empty list if metadata not loaded.
        """
        if not self.metadata:
            return []

        # This is a simplified version
        # Full implementation would parse the metadata structure
        # For now, return empty list (metadata parsing can be added later)
        return []

    def is_valid_combination(self, emoji1: str, emoji2: str) -> Optional[bool]:
        """
        Check if emoji combination exists in metadata.

        Args:
            emoji1: First emoji
            emoji2: Second emoji

        Returns:
            True if combination exists, False if it doesn't, None if metadata not loaded
        """
        if not self.metadata:
            return None

        # Simplified - full implementation would check metadata
        return None

    def get_cache_info(self) -> dict:
        """
        Get information about metadata cache.

        Returns:
            Dictionary with cache information
        """
        if self.cache_file.exists():
            stat = self.cache_file.stat()
            return {
                'exists': True,
                'path': str(self.cache_file),
                'size_mb': stat.st_size / (1024 * 1024),
                'loaded': self.metadata is not None
            }
        else:
            return {
                'exists': False,
                'path': str(self.cache_file),
                'loaded': False
            }
