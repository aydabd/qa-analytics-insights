"""Tests for result_analyzer module."""

from unittest.mock import Mock, patch

import pytest
from qa_analytics_insights.result_analyzer import ResultAnalyzer


class TestResultAnalyzer:
    """Test ResultAnalyzer class."""

    @patch('qa_analytics_insights.result_analyzer.XMLProcessor')
    def test_result_analyzer_init(self, mock_xml_processor):
        """Test ResultAnalyzer initialization."""
        analyzer = ResultAnalyzer("/test/path", num_threads=5)

        assert analyzer.path == "/test/path"
        assert analyzer.num_threads == 5
        mock_xml_processor.assert_called_once_with("/test/path")

    @patch('qa_analytics_insights.result_analyzer.XMLProcessor')
    def test_suites_property(self, mock_xml_processor):
        """Test suites property returns processed test suites."""
        mock_processor = Mock()
        mock_processor.test_suites = ["suite1", "suite2"]
        mock_xml_processor.return_value = mock_processor

        analyzer = ResultAnalyzer("/test/path")
        analyzer.process_test_results = Mock()

        suites = analyzer.suites

        analyzer.process_test_results.assert_called_once()
        assert suites == ["suite1", "suite2"]

    @patch('qa_analytics_insights.result_analyzer.XMLProcessor')
    def test_suites_property_caching(self, mock_xml_processor):
        """Test that suites property caches results."""
        mock_processor = Mock()
        mock_processor.test_suites = ["suite1", "suite2"]
        mock_xml_processor.return_value = mock_processor

        analyzer = ResultAnalyzer("/test/path")
        analyzer.process_test_results = Mock()

        # Access suites twice
        suites1 = analyzer.suites
        suites2 = analyzer.suites

        # process_test_results should only be called once
        analyzer.process_test_results.assert_called_once()
        assert suites1 == suites2

    @patch('qa_analytics_insights.result_analyzer.XMLProcessor')
    def test_classes_property(self, mock_xml_processor):
        """Test classes property returns test classes."""
        mock_processor = Mock()
        mock_processor.test_suites = [Mock(test_classes=["class1", "class2"])]
        mock_xml_processor.return_value = mock_processor

        analyzer = ResultAnalyzer("/test/path")
        analyzer.process_test_results = Mock()

        classes = analyzer.classes

        assert classes == ["class1", "class2"]

    @patch('qa_analytics_insights.result_analyzer.XMLProcessor')
    def test_test_cases_property(self, mock_xml_processor):
        """Test test_cases property returns all test cases."""
        # Create mock test classes with test cases
        mock_class1 = Mock()
        mock_class1.test_cases = ["test1", "test2"]
        mock_class2 = Mock()
        mock_class2.test_cases = ["test3", "test4"]

        mock_suite = Mock()
        mock_suite.test_classes = [mock_class1, mock_class2]
        mock_suite.test_cases = ["test5"]

        mock_processor = Mock()
        mock_processor.test_suites = [mock_suite]
        mock_xml_processor.return_value = mock_processor

        analyzer = ResultAnalyzer("/test/path")
        analyzer.process_test_results = Mock()

        test_cases = analyzer.test_cases

        # Should include all test cases from classes plus suite-level test cases
        assert "test1" in test_cases
        assert "test2" in test_cases
        assert "test3" in test_cases
        assert "test4" in test_cases
        assert "test5" in test_cases

    @patch('qa_analytics_insights.result_analyzer.XMLProcessor')
    def test_process_test_results(self, mock_xml_processor):
        """Test process_test_results method."""
        mock_processor = Mock()
        mock_xml_processor.return_value = mock_processor

        analyzer = ResultAnalyzer("/test/path", num_threads=8)
        analyzer.process_test_results()

        mock_processor.process_files_in_parallel.assert_called_once_with(8)

    @patch('qa_analytics_insights.result_analyzer.XMLProcessor')
    def test_get_slowest_test_classes(self, mock_xml_processor):
        """Test get_slowest_test_classes method."""
        # Create mock test classes with different execution times
        mock_class1 = Mock()
        mock_class1.execution_time = 10.0
        mock_class1.name = "FastClass"

        mock_class2 = Mock()
        mock_class2.execution_time = 20.0
        mock_class2.name = "SlowClass"

        mock_processor = Mock()
        mock_processor.test_suites = [Mock(test_classes=[mock_class1, mock_class2])]
        mock_xml_processor.return_value = mock_processor

        analyzer = ResultAnalyzer("/test/path")
        analyzer.process_test_results = Mock()

        slowest = analyzer.get_slowest_test_classes()

        # Should return classes sorted by execution time (slowest first)
        assert len(slowest) == 2
        assert slowest[0].name == "SlowClass"
        assert slowest[1].name == "FastClass"

    @patch('qa_analytics_insights.result_analyzer.XMLProcessor')
    def test_get_slowest_test_classes_with_limit(self, mock_xml_processor):
        """Test get_slowest_test_classes with limit parameter."""
        # Create multiple mock test classes
        classes = []
        for i in range(5):
            mock_class = Mock()
            mock_class.execution_time = float(i + 1)
            mock_class.name = f"Class{i}"
            classes.append(mock_class)

        mock_processor = Mock()
        mock_processor.test_suites = [Mock(test_classes=classes)]
        mock_xml_processor.return_value = mock_processor

        analyzer = ResultAnalyzer("/test/path")
        analyzer.process_test_results = Mock()

        slowest = analyzer.get_slowest_test_classes(limit=3)

        # Should return only 3 slowest classes
        assert len(slowest) == 3
        assert slowest[0].execution_time == 5.0
        assert slowest[1].execution_time == 4.0
        assert slowest[2].execution_time == 3.0
