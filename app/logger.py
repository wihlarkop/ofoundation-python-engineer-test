"""Centralized logging configuration.

Provides a consistent logger setup across the application.
Configures log format, level, and handlers.
"""

import logging
import sys

from app.config import settings


def setup_logger(name: str) -> logging.Logger:
    """Set up and return a logger with consistent configuration.

    Args:
        name: Logger name (usually __name__ of the module)

    Returns:
        Configured logger instance

    Example:
        from app.logger import setup_logger
        logger = setup_logger(__name__)
        logger.info("Application started")
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        # Set log level based on debug mode
        log_level = logging.DEBUG if settings.debug else logging.INFO
        logger.setLevel(log_level)

        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)

        # Create formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

        # Prevent propagation to root logger
        logger.propagate = False

    return logger


# Application-wide logger
logger = setup_logger("app")
