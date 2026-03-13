"""
Logging configuration for the trading bot.
Sets up file and console logging with appropriate formatting.
"""

import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logging(log_dir: str = "logs", log_level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return the main logger for the trading bot.
    
    Args:
        log_dir: Directory to store log files
        log_level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("trading_bot")
    logger.setLevel(log_level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_formatter = logging.Formatter(
        fmt="%(levelname)-8s | %(message)s"
    )
    
    # File handler - daily rotating log file
    log_filename = f"trading_bot_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(
        log_path / log_filename,
        encoding="utf-8"
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_logger() -> logging.Logger:
    """Get the trading bot logger instance."""
    return logging.getLogger("trading_bot")
