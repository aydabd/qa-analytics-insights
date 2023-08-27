"""Copyright (c) 2023, Aydin Abdi.

This module is responsible for fetching paths from the given initial path.
"""
from pathlib import Path
from queue import Queue

from loguru import logger


class PathFetcher:
    """Responsible for fetching paths from the given initial path.

    Example:
        PathFetcher(initial_path='path/to/initial/path')
    """

    def __init__(self, initial_path: str) -> None:
        """Responsible for fetching paths from the given initial path.

        Args:
            initial_path: Initial path to fetch paths from.
        """
        self.initial_path = Path(initial_path)
        self.queue = Queue()  # type: Queue[Path]

    def fetch_paths(self) -> Queue[Path]:
        """Fetches paths from the given initial path.

        Returns:
            Queue of paths.
        """
        try:
            if self.initial_path.is_file():
                self.queue.put(self.initial_path)
            elif self.initial_path.is_dir():
                for file_path in self.initial_path.iterdir():
                    self.queue.put(file_path)
            else:
                logger.error(f"Invalid path: {self.initial_path}")
        except Exception as e:
            logger.exception(f"Error fetching paths: {str(e)}")
        return self.queue
