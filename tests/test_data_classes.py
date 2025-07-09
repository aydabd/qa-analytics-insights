"""Tests for data_classes module."""

from qa_analytics_insights.data_classes import TestCase, TestClass, TestSuite


class TestTestCase:
    """Test TestCase data class."""

    def test_test_case_init_with_defaults(self):
        """Test TestCase initialization with default values."""
        test_case = TestCase(name="test_example")
        assert test_case.name == "test_example"
        assert test_case.test_module is None
        assert test_case.test_class is None
        assert test_case.execution_time == 0.0
        assert test_case.result == "passed"
        assert test_case.timestamp is None
        assert test_case.failure_reason is None
        assert test_case.error_reason is None
        assert test_case.skipped_reason is None
        assert test_case.system_out is None

    def test_test_case_init_with_values(self):
        """Test TestCase initialization with custom values."""
        test_case = TestCase(
            name="test_example",
            test_module="test_module",
            test_class="TestClass",
            execution_time=1.5,
            result="failed",
            timestamp="2023-01-01T00:00:00",
            failure_reason="assertion error",
            error_reason="runtime error",
            skipped_reason="not applicable",
            system_out="output text",
        )
        assert test_case.name == "test_example"
        assert test_case.test_module == "test_module"
        assert test_case.test_class == "TestClass"
        assert test_case.execution_time == 1.5
        assert test_case.result == "failed"
        assert test_case.timestamp == "2023-01-01T00:00:00"
        assert test_case.failure_reason == "assertion error"
        assert test_case.error_reason == "runtime error"
        assert test_case.skipped_reason == "not applicable"
        assert test_case.system_out == "output text"


class TestTestClass:
    """Test TestClass data class."""

    def test_test_class_init_empty(self):
        """Test TestClass initialization with no test cases."""
        test_class = TestClass(name="TestExample")
        assert test_class.name == "TestExample"
        assert test_class.test_cases == []
        assert test_class.passed == 0
        assert test_class.failed == 0
        assert test_class.skipped == 0
        assert test_class.errors == 0
        assert test_class.execution_time == 0.0
        assert test_class.failed_test_cases == []
        assert test_class.skipped_test_cases == []
        assert test_class.error_test_cases == []

    def test_test_class_with_passed_test_cases(self):
        """Test TestClass with passed test cases."""
        test_case1 = TestCase(name="test1", execution_time=1.0, result="passed")
        test_case2 = TestCase(name="test2", execution_time=2.0, result="passed")
        test_class = TestClass(name="TestExample", test_cases=[test_case1, test_case2])

        assert test_class.passed == 2
        assert test_class.failed == 0
        assert test_class.skipped == 0
        assert test_class.errors == 0
        assert test_class.execution_time == 3.0

    def test_test_class_with_failed_test_cases(self):
        """Test TestClass with failed test cases."""
        test_case1 = TestCase(name="test1", execution_time=1.0, result="failed")
        test_case2 = TestCase(name="test2", execution_time=2.0, result="failed")
        test_class = TestClass(name="TestExample", test_cases=[test_case1, test_case2])

        assert test_class.passed == 0
        assert test_class.failed == 2
        assert test_class.skipped == 0
        assert test_class.errors == 0
        assert test_class.execution_time == 3.0
        assert len(test_class.failed_test_cases) == 2

    def test_test_class_with_skipped_test_cases(self):
        """Test TestClass with skipped test cases."""
        test_case1 = TestCase(name="test1", execution_time=1.0, result="skipped")
        test_class = TestClass(name="TestExample", test_cases=[test_case1])

        assert test_class.passed == 0
        assert test_class.failed == 0
        assert test_class.skipped == 1
        assert test_class.errors == 0
        assert len(test_class.skipped_test_cases) == 1

    def test_test_class_with_error_test_cases(self):
        """Test TestClass with error test cases."""
        test_case1 = TestCase(name="test1", execution_time=1.0, result="error")
        test_class = TestClass(name="TestExample", test_cases=[test_case1])

        assert test_class.passed == 0
        assert test_class.failed == 0
        assert test_class.skipped == 0
        assert test_class.errors == 1
        assert len(test_class.error_test_cases) == 1


class TestTestSuite:
    """Test TestSuite data class."""

    def test_test_suite_init_with_defaults(self):
        """Test TestSuite initialization with default values."""
        test_suite = TestSuite()
        assert test_suite.name is None
        assert test_suite.tests == 0
        assert test_suite.errors == 0
        assert test_suite.failures == 0
        assert test_suite.skipped == 0
        assert test_suite.execution_time == 0.0
        assert test_suite.timestamp is None
        assert test_suite.test_classes == []
        assert test_suite.test_cases == []
        assert test_suite.passed == 0

    def test_test_suite_init_with_values(self):
        """Test TestSuite initialization with custom values."""
        test_suite = TestSuite(
            name="test_suite",
            tests=10,
            errors=1,
            failures=2,
            skipped=1,
            execution_time=15.5,
            timestamp="2023-01-01T00:00:00",
        )
        assert test_suite.name == "test_suite"
        assert test_suite.tests == 10
        assert test_suite.errors == 1
        assert test_suite.failures == 2
        assert test_suite.skipped == 1
        assert test_suite.execution_time == 15.5
        assert test_suite.timestamp == "2023-01-01T00:00:00"
        assert test_suite.passed == 6  # 10 - 1 - 2 - 1 = 6

    def test_test_suite_passed_calculation(self):
        """Test TestSuite passed tests calculation."""
        test_suite = TestSuite(tests=20, errors=3, failures=5, skipped=2)
        assert test_suite.passed == 10  # 20 - 3 - 5 - 2 = 10
