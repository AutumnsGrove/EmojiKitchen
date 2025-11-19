"""Emoji Kitchen - Download emoji combinations from Google's Emoji Kitchen."""

__version__ = "1.0.0"
__author__ = "Claude Code"
__description__ = "CLI tool for downloading emoji combinations from Google's Emoji Kitchen"

from .orchestrator import DownloadOrchestrator, DownloadStats
from .api.client import EmojiKitchenClient
from .storage.manager import StorageManager
from .utils.json_logger import JSONLogger

__all__ = [
    'DownloadOrchestrator',
    'DownloadStats',
    'EmojiKitchenClient',
    'StorageManager',
    'JSONLogger',
]
