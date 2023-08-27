"""Copyright (c) 2023, Aydin Abdi.

This file contains the data classes used in the qa-analytics-insights package.
"""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TestCase:
    """Represents a test case.

    Args:
        name: Name of the test case.
        test_module: Name of the test module.
        test_class: Name of the test class.
        execution_time: Execution time of the test case.
        result: Result of the test case.
        timestamp: Timestamp of the test case.
        failure_reason: Failure reason of the test case.
        skipped_reason: Skipped reason of the test case.
        system_out: System out of the test case.
    """

    name: str
    test_module: Optional[str] = None
    test_class: Optional[str] = None
    execution_time: float = 0.0
    result: str = "passed"
    timestamp: Optional[str] = None
    failure_reason: Optional[str] = None
    error_reason: Optional[str] = None
    skipped_reason: Optional[str] = None
    system_out: Optional[str] = None


@dataclass
class TestClass:
    """Represents a test class.

    Args:
        name: Name of the test class.
        test_cases: List of test cases in the test class.
        passed: Number of passed tests in the test class.
        failed: Number of failed tests in the test class.
        skipped: Number of skipped tests in the test class.
        errors: Number of errors in the test class.
        execution_time: Execution time of the test class.
        failed_test_cases: List of failed test cases in the test class.
        skipped_test_cases: List of skipped test cases in the test class.
        error_test_cases: List of error test cases in the test class.
    """

    name: str
    test_cases: List[TestCase] = field(default_factory=list)
    passed: int = field(init=False, default=0)
    failed: int = field(init=False, default=0)
    skipped: int = field(init=False, default=0)
    errors: int = field(init=False, default=0)
    execution_time: float = field(init=False, default=0.0)
    failed_test_cases: List[TestCase] = field(init=False, default_factory=list)
    skipped_test_cases: List[TestCase] = field(init=False, default_factory=list)
    error_test_cases: List[TestCase] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        """Post initialization method.

        This method calculates the number of passed, failed, skipped and
        error tests in the test class.
        """
        with ThreadPoolExecutor() as executor:
            executor.map(self._calculate_test_class_metrics, self.test_cases)

    def _calculate_test_class_metrics(self, test_case: TestCase) -> None:
        """Calculates the number of passed, failed, skipped and
        error tests in the test class.

        Args:
            test_case: Test case to be analyzed.
        """
        if test_case.result == "passed":
            self.passed += 1
        if test_case.result == "failed":
            self.failed += 1
            self.failed_test_cases.append(test_case)
        if test_case.result == "skipped":
            self.skipped += 1
            self.skipped_test_cases.append(test_case)
        if test_case.result == "error":
            self.errors += 1
            self.error_test_cases.append(test_case)

        self.execution_time += test_case.execution_time


@dataclass
class TestSuite:
    """Represents a test suite.

    Args:
        name: Name of the test suite.
        tests: Total number of tests.
        errors: Total number of errors.
        failures: Total number of failures.
        skipped: Total number of skipped tests.
        execution_time: Total execution time of the test suite.
        timestamp: Timestamp of the test suite.
        test_classes: List of test classes in the test suite.
        test_cases: List of ungrouped test cases in the test suite.
        passed: Number of passed tests in the test suite.
    """

    name: Optional[str] = field(default=None)
    tests: int = field(default=0)
    errors: int = field(default=0)
    failures: int = field(default=0)
    skipped: int = field(default=0)
    execution_time: float = field(default=0.0)
    timestamp: Optional[str] = field(default=None)
    test_classes: List[TestClass] = field(default_factory=list)
    test_cases: List[TestCase] = field(default_factory=list)
    passed: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        """Calculates the number of passed tests in the test suite."""
        self.passed = self.tests - self.errors - self.failures - self.skipped
