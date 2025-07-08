"""Tests for the result visualizer module."""

import pytest
from unittest.mock import Mock, patch
import matplotlib.pyplot as plt

from qa_analytics_insights.result_visualizer import ResultVisualizer
from qa_analytics_insights.data_classes import TestCase, TestClass, TestSuite


@pytest.fixture
def sample_test_cases():
    """Create sample test cases with long class names."""
    return [
        TestCase(
            name="test_method_1",
            test_class="VeryLongTestClassNameThatExceedsSixteenCharacters",
            execution_time=1.5,
            result="passed"
        ),
        TestCase(
            name="test_method_2", 
            test_class="VeryLongTestClassNameThatExceedsSixteenCharacters",
            execution_time=2.0,
            result="failed",
            failure_reason="AssertionError: Test failed"
        ),
        TestCase(
            name="test_method_3",
            test_class="AnotherVeryLongTestClassNameThatIsEvenLongerThanSixteenCharacters",
            execution_time=0.5,
            result="skipped",
            skipped_reason="Test skipped for some reason"
        ),
        TestCase(
            name="test_method_4",
            test_class="ShortClass",
            execution_time=1.0,
            result="passed"
        )
    ]


@pytest.fixture
def sample_test_classes(sample_test_cases):
    """Create sample test classes with long names."""
    class1 = TestClass(name="VeryLongTestClassNameThatExceedsSixteenCharacters")
    class1.test_cases = [sample_test_cases[0], sample_test_cases[1]]
    
    class2 = TestClass(name="AnotherVeryLongTestClassNameThatIsEvenLongerThanSixteenCharacters")
    class2.test_cases = [sample_test_cases[2]]
    
    class3 = TestClass(name="ShortClass") 
    class3.test_cases = [sample_test_cases[3]]
    
    return [class1, class2, class3]


@pytest.fixture 
def sample_test_suites(sample_test_classes, sample_test_cases):
    """Create sample test suites."""
    suite = TestSuite(
        name="VeryLongTestSuiteNameThatAlsoExceedsSixteenCharacters",
        tests=4,
        failures=1,
        errors=0,
        skipped=1,
        execution_time=5.0
    )
    suite.test_classes = sample_test_classes
    suite.test_cases = sample_test_cases
    return [suite]


class TestResultVisualizer:
    """Test class for ResultVisualizer."""

    def test_pie_charts_with_long_class_names(self, sample_test_suites):
        """Test that pie charts handle long class names properly."""
        visualizer = ResultVisualizer(sample_test_suites)
        
        # This should not raise an exception and should handle long names
        figure = visualizer.plot_pie_charts_test_classes()
        
        assert figure is not None
        plt.close(figure)

    def test_failed_test_cases_table_with_long_names(self, sample_test_suites):
        """Test that failed test cases table handles long class names."""
        visualizer = ResultVisualizer(sample_test_suites)
        
        figure = visualizer.plot_failed_test_cases_table()
        
        assert figure is not None
        plt.close(figure)

    def test_skipped_test_cases_table_with_long_names(self, sample_test_suites):
        """Test that skipped test cases table handles long class names.""" 
        visualizer = ResultVisualizer(sample_test_suites)
        
        figure = visualizer.plot_skipped_test_cases_table()
        
        assert figure is not None
        plt.close(figure)

    def test_slowest_test_classes_chart_with_long_names(self, sample_test_classes):
        """Test that slowest test classes chart handles long class names."""
        visualizer = ResultVisualizer()
        
        figure = visualizer.plot_top_slowest_test_classes_pie_bar_chart(sample_test_classes)
        
        assert figure is not None
        plt.close(figure)

    def test_test_suites_summary_table_with_long_names(self, sample_test_suites):
        """Test that test suites summary table handles long names."""
        visualizer = ResultVisualizer(sample_test_suites)
        
        figure = visualizer.plot_test_suites_summary_table()
        
        assert figure is not None
        plt.close(figure)

    def test_truncate_long_name_function(self):
        """Test utility function for truncating long names."""
        visualizer = ResultVisualizer()
        
        # Test normal case (no truncation needed)
        short_name = "ShortName"
        assert visualizer.truncate_name(short_name) == short_name
        
        # Test exact length (no truncation)
        exact_name = "ExactlySixteenCh"  # 16 characters
        assert visualizer.truncate_name(exact_name) == exact_name
        
        # Test long name (truncation needed)
        long_name = "VeryLongTestClassNameThatExceedsSixteenCharacters"
        truncated = visualizer.truncate_name(long_name)
        assert len(truncated) == 16
        assert truncated.endswith("...")
        assert truncated == "VeryLongTestC..."
        
        # Test None input
        assert visualizer.truncate_name(None) == "N/A"
        
        # Test custom max length
        assert visualizer.truncate_name("TooLongName", max_length=8) == "TooLo..."