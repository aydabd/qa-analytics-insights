"""Copyright (c) 2023, Aydin Abdi.

Unit tests for log.py module.
"""
import time

from qa_analytics_insights.log import (
    default_logging,
    log_execution_time,
    verbose_logging,
)


def test_default_logging() -> None:
    """Test default_logging function."""
    assert default_logging() is None


def test_verbose_logging() -> None:
    """Test verbose_logging function."""
    assert verbose_logging() is None


def test_log_execution_time() -> None:
    """Test log_execution_time decorator."""

    @log_execution_time
    def execution_time_func() -> None:
        """Test function."""
        time.sleep(1)

    execution_time_func()
