"""Copyright (c) 2023, Aydin Abdi.

This module is responsible for logging.
"""
import functools
import sys
import time
from typing import Any, Callable

from loguru import logger


def verbose_logging() -> None:
    """loguru verbose."""
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
    logger.add("outputs/qa_analytics_insights.log", level="DEBUG", rotation="1 day")


def default_logging() -> None:
    """loguru default."""
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    logger.add("outputs/qa_analytics_insights.log", level="DEBUG", rotation="1 day")


def log_execution_time(method: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to log the time execution of a method.

    Args:
        method: The method to be decorated.

    Returns:
        The decorated method.
    """

    @functools.wraps(method)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Wrapper function to log the time execution of a method.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The result of the method.
        """
        start = time.time()
        result = method(*args, **kwargs)
        end = time.time()
        duration = end - start

        logger.info(f"{method.__name__} executed in {duration:.2f} seconds.")
        return result

    return wrapper
