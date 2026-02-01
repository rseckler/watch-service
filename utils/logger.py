"""
Logging utility with emoji indicators for Watch Service
"""
import logging
import sys
from datetime import datetime
from pathlib import Path


class EmojiFormatter(logging.Formatter):
    """Custom formatter with emoji indicators"""

    EMOJI_MAP = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️ ',
        'WARNING': '⚠️ ',
        'ERROR': '❌',
        'CRITICAL': '🚨'
    }

    def format(self, record):
        emoji = self.EMOJI_MAP.get(record.levelname, '  ')
        record.emoji = emoji
        return super().format(record)


def setup_logger(name: str, log_file: str = None, level=logging.INFO):
    """
    Setup logger with console and optional file output

    Args:
        name: Logger name
        log_file: Optional log file path
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Console handler with emoji
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = EmojiFormatter(
        '%(emoji)s %(asctime)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (no emoji)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str):
    """Get existing logger or create new one"""
    return logging.getLogger(name)
