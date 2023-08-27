"""Copyright (c) 2023, Aydin Abdi.

This module processes files in the given path in parallel and
puts the xml files in a queue for further processing.
"""
import threading
from queue import Queue
from typing import List  # noqa: F401

from qa_analytics_insights.data_classes import TestSuite  # noqa: F401
from qa_analytics_insights.patch_fetcher import PathFetcher
from qa_analytics_insights.xml_filter import XMLFilter
from qa_analytics_insights.xml_loader import XMLLoader
from qa_analytics_insights.xml_parser import XMLParser
from qa_analytics_insights.xml_tag_finder import XMLTagFinder


class XMLProcessor:
    """Responsible for processing files into xml queues.

    Args:
        path: Path to the XML files.
    """

    def __init__(self, path: str) -> None:
        """Responsible for processing XML files in the given path.

        Args:
            path: Path to the XML files.
        """
        self.path = path
        self.test_suites = []  # type: List[TestSuite]
        self.lock = threading.Lock()  # type: threading.Lock

    def process_files_in_parallel(self, num_threads: int) -> None:
        """Processes the XML files in the given path in parallel.

        Args:
            num_threads: Number of threads to use for processing.
        """
        file_fetcher = PathFetcher(self.path)
        file_queue = file_fetcher.fetch_paths()
        xml_filter = XMLFilter(file_queue)
        xml_queue = xml_filter.filter_xml()
        threads = []

        for _ in range(num_threads):
            thread = threading.Thread(target=self._process_xml, args=(xml_queue,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def _process_xml(self, xml_queue: Queue[str]) -> None:
        """Processes the XML files in the given path.

        Args:
            xml_queue: Queue of XML files to process.
        """
        while not xml_queue.empty():
            xml_path = xml_queue.get()
            xml_loader = XMLLoader(xml_path)
            xml_tag_finder = XMLTagFinder(xml_loader)
            xml_parser = XMLParser(xml_tag_finder)
            test_suite = xml_parser.parse()

            with self.lock:
                self.test_suites.append(test_suite)
