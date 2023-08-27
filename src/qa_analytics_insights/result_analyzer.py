"""Copyright (c) 2023, Aydin Abdi.

ResultAnalyzer implements the logic for analyzing the test results with
different metrics which can be used to visualize the results.
"""
from typing import List

from qa_analytics_insights.data_classes import TestCase, TestClass, TestSuite
from qa_analytics_insights.xml_processor import XMLProcessor


class ResultAnalyzer:
    """Analyzes the test results with several metrics.

    Example:
        - slowest_test_classes
        - slowest_test_cases
        - failed_test_cases with failure_reason
        - skipped_test_cases with skipped_reason
        - execution times by test class in descending order
    """

    def __init__(self, path: str, num_threads: int = 10) -> None:
        """Initialize the ResultAnalyzer.

        Args:
            path: Path to the test result XML files.
            num_threads: Number of threads to use for parsing the XML files.
        """
        self.path = path
        self.num_threads = num_threads
        self.processor = XMLProcessor(self.path)
        self._suites = []  # type: List[TestSuite]
        self._classes = []  # type: List[TestClass]
        self._test_cases = []  # type: List[TestCase]

    @property
    def suites(self) -> List[TestSuite]:
        """Return the test suites.

        Returns:
            List of TestSuite objects.
        """
        if not self._suites:
            self.process_test_results()
            self._suites = self.processor.test_suites
        return self._suites

    @property
    def classes(self) -> List[TestClass]:
        """Return the test classes.

        Returns:
            List of TestClass objects.
        """
        if not self._classes:
            for test_suite in self.suites:
                self._classes.extend(test_suite.test_classes)
        return self._classes

    @property
    def test_cases(self) -> List[TestCase]:
        """Return the test cases for all test suites.

        Ungrouped test cases are also included.

        Returns:
            List of TestCase objects.
        """
        if not self._test_cases:
            for test_suite in self.suites:
                self._test_cases.extend(test_suite.test_cases)
                for test_class in self.classes:
                    self._test_cases.extend(test_class.test_cases)
        return self._test_cases

    def process_test_results(self) -> None:
        """Process the test result XML files and parse them into TestClass objects.

        Returns:
            List of TestSuites objects.
        """
        self.processor.process_files_in_parallel(self.num_threads)

    def __len__(self) -> int:
        """Return the number of TestClass objects.

        Returns:
            Number of TestClass objects.
        """
        return len(self.test_cases)

    def get_execution_times_by_test_class_in_descending_order(self) -> List[TestClass]:
        """Return the test classes sorted by execution time in descending order.

        Returns:
            List of TestClass objects.
        """
        return sorted(
            self.classes,
            key=lambda test_class: test_class.execution_time,
            reverse=True,
        )

    def get_slowest_test_classes(self, num_test_classes: int = 10) -> List[TestClass]:
        """Return the slowest test classes.

        Args:
            num_test_classes: Number of test classes to return.

        Returns:
            List of TestClass objects.
        """
        return self.get_execution_times_by_test_class_in_descending_order()[
            :num_test_classes
        ]
