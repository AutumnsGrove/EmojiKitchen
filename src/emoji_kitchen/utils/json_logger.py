"""JSON logging suite for tracking download successes and failures."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import sys


@dataclass
class DownloadResult:
    """Record of a single download attempt."""

    emoji1: str
    emoji2: str
    timestamp: str
    success: bool
    file_path: Optional[str] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None
    duration_ms: Optional[float] = None
    url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class JSONLogger:
    """
    Comprehensive JSON logging system with separate success/failure tracking.

    Features:
    - Separate JSON files for successes and failures
    - Regular Python logging for debugging
    - Session-based organization
    - Real-time file updates
    """

    def __init__(
        self,
        log_dir: Path,
        session_id: Optional[str] = None,
        enable_console: bool = True,
        log_level: int = logging.INFO
    ):
        """
        Initialize JSON logger.

        Args:
            log_dir: Directory for log files
            session_id: Unique session identifier (auto-generated if None)
            enable_console: Enable console logging
            log_level: Python logging level
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Generate session ID if not provided
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = session_id

        # Define log file paths
        self.success_file = self.log_dir / f"successes_{self.session_id}.json"
        self.failure_file = self.log_dir / f"failures_{self.session_id}.json"
        self.debug_file = self.log_dir / f"debug_{self.session_id}.log"

        # Initialize JSON files with empty lists
        self._init_json_file(self.success_file)
        self._init_json_file(self.failure_file)

        # Set up Python logger for debugging
        self.logger = logging.getLogger(f"emoji_kitchen_{session_id}")
        self.logger.setLevel(log_level)
        self.logger.handlers.clear()  # Clear any existing handlers

        # File handler for debug logs
        file_handler = logging.FileHandler(self.debug_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console handler (optional)
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            console_formatter = logging.Formatter('%(levelname)s: %(message)s')
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

        # In-memory storage for session summary
        self.successes: List[DownloadResult] = []
        self.failures: List[DownloadResult] = []

        self.logger.info(f"JSON Logger initialized - Session: {self.session_id}")
        self.logger.info(f"Success log: {self.success_file}")
        self.logger.info(f"Failure log: {self.failure_file}")
        self.logger.info(f"Debug log: {self.debug_file}")

    def _init_json_file(self, file_path: Path) -> None:
        """Initialize JSON file with empty array."""
        if not file_path.exists():
            with file_path.open('w', encoding='utf-8') as f:
                json.dump([], f)

    def _append_to_json_file(self, file_path: Path, result: DownloadResult) -> None:
        """Append a result to JSON file."""
        try:
            # Read existing data
            with file_path.open('r', encoding='utf-8') as f:
                data = json.load(f)

            # Append new result
            data.append(result.to_dict())

            # Write back
            with file_path.open('w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Failed to write to {file_path}: {e}")

    def log_success(
        self,
        emoji1: str,
        emoji2: str,
        file_path: str,
        duration_ms: Optional[float] = None,
        url: Optional[str] = None,
        status_code: int = 200
    ) -> None:
        """
        Log a successful download.

        Args:
            emoji1: First emoji
            emoji2: Second emoji
            file_path: Path where file was saved
            duration_ms: Download duration in milliseconds
            url: Download URL
            status_code: HTTP status code
        """
        result = DownloadResult(
            emoji1=emoji1,
            emoji2=emoji2,
            timestamp=datetime.now().isoformat(),
            success=True,
            file_path=file_path,
            status_code=status_code,
            duration_ms=duration_ms,
            url=url
        )

        self.successes.append(result)
        self._append_to_json_file(self.success_file, result)

        self.logger.info(
            f"SUCCESS: {emoji1} + {emoji2} ’ {file_path} "
            f"({duration_ms:.0f}ms)" if duration_ms else ""
        )

    def log_failure(
        self,
        emoji1: str,
        emoji2: str,
        error_type: str,
        error_message: str,
        status_code: Optional[int] = None,
        duration_ms: Optional[float] = None,
        url: Optional[str] = None
    ) -> None:
        """
        Log a failed download.

        Args:
            emoji1: First emoji
            emoji2: Second emoji
            error_type: Type of error (e.g., "HTTPError", "NetworkError", "404")
            error_message: Detailed error message
            status_code: HTTP status code (if applicable)
            duration_ms: Attempt duration in milliseconds
            url: Download URL
        """
        result = DownloadResult(
            emoji1=emoji1,
            emoji2=emoji2,
            timestamp=datetime.now().isoformat(),
            success=False,
            error_type=error_type,
            error_message=error_message,
            status_code=status_code,
            duration_ms=duration_ms,
            url=url
        )

        self.failures.append(result)
        self._append_to_json_file(self.failure_file, result)

        self.logger.warning(
            f"FAILURE: {emoji1} + {emoji2} - {error_type}: {error_message} "
            f"[HTTP {status_code}]" if status_code else ""
        )

    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)

    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get session summary statistics.

        Returns:
            Dictionary with success/failure counts and rates
        """
        total = len(self.successes) + len(self.failures)
        success_count = len(self.successes)
        failure_count = len(self.failures)

        success_rate = (success_count / total * 100) if total > 0 else 0.0

        return {
            'session_id': self.session_id,
            'total_attempts': total,
            'successes': success_count,
            'failures': failure_count,
            'success_rate': f"{success_rate:.1f}%",
            'success_file': str(self.success_file),
            'failure_file': str(self.failure_file),
            'debug_file': str(self.debug_file)
        }

    def save_summary(self) -> None:
        """Save session summary to JSON file."""
        summary_file = self.log_dir / f"summary_{self.session_id}.json"
        summary = self.get_summary()

        # Add breakdown by error type
        error_breakdown: Dict[str, int] = {}
        for failure in self.failures:
            error_type = failure.error_type or 'Unknown'
            error_breakdown[error_type] = error_breakdown.get(error_type, 0) + 1

        summary['error_breakdown'] = error_breakdown

        with summary_file.open('w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Summary saved to {summary_file}")

    def close(self) -> None:
        """Close logger and save final summary."""
        self.save_summary()
        self.logger.info("JSON Logger closed")
