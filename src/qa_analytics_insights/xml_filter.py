"""Copyright (c) 2023, Aydin Abdi.

This module filters XML files from the given path queue.
"""
from pathlib import Path
from queue import Queue

from loguru import logger


class XMLFilter:
    """Responsible for filtering XML files from the given path queue."""

    def __init__(self, path_queue: Queue[Path]) -> None:
        """Responsible for filtering XML files from the given path queue.

        Args:
            path_queue: Queue of paths to filter XML files from.
        """
        self.path_queue = path_queue
        self.xml_queue = Queue()  # type: Queue[Path]

    def filter_xml(self) -> Queue[Path]:
        """Filters XML files from the given path queue.

        Returns:
            Queue of XML files.
        """
        try:
            while not self.path_queue.empty():
                path = self.path_queue.get()
                if path.suffix == ".xml":
                    self.xml_queue.put(path)
                else:
                    logger.debug(f"Skipped non-XML file: {path}")
        except Exception as unknown_error:  # pragma: no cover
            logger.exception(f"Error filtering XML files: {unknown_error}")
        return self.xml_queue
