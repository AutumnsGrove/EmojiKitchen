"""Storage manager for downloading and organizing emoji combination files."""

from pathlib import Path
from typing import Optional
from .paths import generate_full_path, FilenameFormat


class StorageManager:
    """
    Manages file storage for emoji combination images.

    Features:
    - Cross-platform filename compatibility
    - Directory organization by base emoji
    - Duplicate detection (skip existing files)
    - Automatic directory creation
    """

    def __init__(
        self,
        base_dir: Path,
        filename_format: FilenameFormat = 'auto'
    ):
        """
        Initialize storage manager.

        Args:
            base_dir: Base directory for downloads
            filename_format: Filename format ('emoji', 'codepoint', or 'auto')
        """
        self.base_dir = Path(base_dir)
        self.filename_format = filename_format

        # Create base directory
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_file_path(self, emoji1: str, emoji2: str) -> Path:
        """
        Get file path for emoji combination.

        Args:
            emoji1: First emoji
            emoji2: Second emoji

        Returns:
            Path object for the file
        """
        return generate_full_path(
            self.base_dir,
            emoji1,
            emoji2,
            self.filename_format
        )

    def file_exists(self, emoji1: str, emoji2: str) -> bool:
        """
        Check if file already exists.

        Args:
            emoji1: First emoji
            emoji2: Second emoji

        Returns:
            True if file exists, False otherwise
        """
        path = self.get_file_path(emoji1, emoji2)
        return path.exists() and path.is_file()

    def save(
        self,
        emoji1: str,
        emoji2: str,
        content: bytes
    ) -> Path:
        """
        Save emoji combination image to disk.

        Args:
            emoji1: First emoji
            emoji2: Second emoji
            content: Image binary content

        Returns:
            Path where file was saved

        Raises:
            IOError: If file cannot be written
        """
        file_path = self.get_file_path(emoji1, emoji2)

        # Create parent directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        file_path.write_bytes(content)

        return file_path

    def get_file_size(self, emoji1: str, emoji2: str) -> Optional[int]:
        """
        Get size of existing file in bytes.

        Args:
            emoji1: First emoji
            emoji2: Second emoji

        Returns:
            File size in bytes, or None if file doesn't exist
        """
        path = self.get_file_path(emoji1, emoji2)
        if path.exists():
            return path.stat().st_size
        return None

    def delete(self, emoji1: str, emoji2: str) -> bool:
        """
        Delete emoji combination file.

        Args:
            emoji1: First emoji
            emoji2: Second emoji

        Returns:
            True if file was deleted, False if it didn't exist
        """
        path = self.get_file_path(emoji1, emoji2)
        if path.exists():
            path.unlink()
            return True
        return False

    def get_emoji_directory(self, emoji: str) -> Path:
        """
        Get directory path for a base emoji.

        Args:
            emoji: Base emoji

        Returns:
            Path to emoji directory
        """
        from .paths import generate_directory_name
        dir_name = generate_directory_name(emoji, self.filename_format)
        return self.base_dir / dir_name

    def count_files(self, emoji: Optional[str] = None) -> int:
        """
        Count downloaded files.

        Args:
            emoji: If provided, count files for this emoji only.
                   If None, count all files.

        Returns:
            Number of files
        """
        if emoji:
            directory = self.get_emoji_directory(emoji)
            if directory.exists():
                return len(list(directory.glob('*.png')))
            return 0
        else:
            return len(list(self.base_dir.rglob('*.png')))
