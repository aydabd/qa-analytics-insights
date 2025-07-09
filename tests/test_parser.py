"""Tests for parser module."""

import re
from unittest.mock import Mock, patch
from xml.etree import ElementTree as ET

import pytest
from qa_analytics_insights.parser import ParserTestCase, ParserTestSuite


class TestParserTestSuite:
    """Test ParserTestSuite class."""

    def test_parse_basic_test_suite(self):
        """Test parsing a basic test suite XML element."""
        xml_content = """
        <testsuite name="TestSuite" tests="5" errors="1" failures="2"
                   skipped="1" time="10.5" timestamp="2023-01-01T00:00:00">
        </testsuite>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestSuite(root)
        test_suite = parser.parse()

        assert test_suite.name == "TestSuite"
        assert test_suite.tests == 5
        assert test_suite.errors == 1
        assert test_suite.failures == 2
        assert test_suite.skipped == 1
        assert test_suite.execution_time == 10.5
        assert test_suite.timestamp == "2023-01-01T00:00:00"

    def test_parse_test_suite_with_skip_attribute(self):
        """Test parsing test suite with 'skip' attribute instead of 'skipped'."""
        xml_content = """
        <testsuite name="TestSuite" tests="3" errors="0" failures="0"
                   skip="1" time="5.0">
        </testsuite>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestSuite(root)
        test_suite = parser.parse()

        assert test_suite.skipped == 1

    def test_parse_test_suite_missing_attributes(self):
        """Test parsing test suite with missing attributes."""
        xml_content = """
        <testsuite name="TestSuite">
        </testsuite>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestSuite(root)
        test_suite = parser.parse()

        assert test_suite.name == "TestSuite"
        assert test_suite.tests == 0
        assert test_suite.errors == 0
        assert test_suite.failures == 0
        assert test_suite.skipped == 0
        assert test_suite.execution_time == 0.0
        assert test_suite.timestamp == ""


class TestParserTestCase:
    """Test ParserTestCase class."""

    def test_parse_basic_test_case(self):
        """Test parsing a basic test case XML element."""
        xml_content = """
        <testcase name="test_example" classname="TestClass"
                  time="1.5" timestamp="2023-01-01T00:00:00">
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)
        test_case = parser.parse()

        assert test_case.name == "test_example"
        assert test_case.test_class == "TestClass"
        assert test_case.execution_time == 1.5
        assert test_case.timestamp == "2023-01-01T00:00:00"
        assert test_case.result == "passed"

    def test_parse_test_case_with_failure(self):
        """Test parsing test case with failure element."""
        xml_content = """
        <testcase name="test_example" classname="TestClass" time="1.5">
            <failure message="assertion failed">
                Detailed failure message here
            </failure>
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)
        test_case = parser.parse()

        assert test_case.result == "failed"
        assert test_case.failure_reason is not None

    def test_parse_test_case_with_error(self):
        """Test parsing test case with error element."""
        xml_content = """
        <testcase name="test_example" classname="TestClass" time="1.5">
            <error message="runtime error">
                Detailed error message here
            </error>
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)
        test_case = parser.parse()

        assert test_case.result == "error"
        assert test_case.error_reason is not None

    def test_parse_test_case_with_skipped(self):
        """Test parsing test case with skipped element."""
        xml_content = """
        <testcase name="test_example" classname="TestClass" time="0.0">
            <skipped message="not applicable">
                Skipped reason here
            </skipped>
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)
        test_case = parser.parse()

        assert test_case.result == "skipped"
        assert test_case.skipped_reason is not None

    def test_parse_test_case_with_system_out(self):
        """Test parsing test case with system-out element."""
        xml_content = """
        <testcase name="test_example" classname="TestClass" time="1.5">
            <system-out>Console output here</system-out>
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)
        test_case = parser.parse()

        assert test_case.system_out == "Console output here"

    def test_parse_test_case_missing_attributes(self):
        """Test parsing test case with missing attributes."""
        xml_content = """
        <testcase name="test_example">
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)
        test_case = parser.parse()

        assert test_case.name == "test_example"
        assert test_case.test_class == ""
        assert test_case.execution_time == 0.0
        assert test_case.timestamp == ""

    @patch('qa_analytics_insights.parser.logger')
    def test_parse_test_case_with_parsing_exception(self, mock_logger):
        """Test handling of parsing exceptions."""
        xml_content = """
        <testcase name="test_example">
            <failure message="test">Some failure</failure>
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)

        # Mock the parsing method to raise an exception
        with patch.object(parser, 'get_failure_reason', side_effect=Exception("parse error")):
            test_case = parser.parse()

            # Should log warning about parsing failure
            assert mock_logger.warning.called

    def test_get_testcase_result_passed(self):
        """Test get_testcase_result for passed test."""
        xml_content = """
        <testcase name="test_example">
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)

        result = parser.get_testcase_result()
        assert result == "passed"

    def test_get_testcase_result_failed(self):
        """Test get_testcase_result for failed test."""
        xml_content = """
        <testcase name="test_example">
            <failure message="test failed">Details</failure>
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)

        result = parser.get_testcase_result()
        assert result == "failed"

    def test_get_testcase_result_error(self):
        """Test get_testcase_result for error test."""
        xml_content = """
        <testcase name="test_example">
            <error message="runtime error">Details</error>
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)

        result = parser.get_testcase_result()
        assert result == "error"

    def test_get_testcase_result_skipped(self):
        """Test get_testcase_result for skipped test."""
        xml_content = """
        <testcase name="test_example">
            <skipped message="not applicable">Details</skipped>
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)

        result = parser.get_testcase_result()
        assert result == "skipped"

    def test_find_tag_attribute_with_attribute(self):
        """Test find_tag_attribute method with attribute."""
        xml_content = """
        <testcase name="test_example">
            <failure message="test failed">Details</failure>
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)

        result = parser.find_tag_attribute("failure", "message")
        assert result == "test failed"

    def test_find_tag_attribute_with_text(self):
        """Test find_tag_attribute method with text."""
        xml_content = """
        <testcase name="test_example">
            <failure message="test failed">Failure details</failure>
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)

        result = parser.find_tag_attribute("failure")
        assert result == "Failure details"

    def test_find_tag_attribute_tag_not_found(self):
        """Test find_tag_attribute method when tag is not found."""
        xml_content = """
        <testcase name="test_example">
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)

        result = parser.find_tag_attribute("failure")
        assert result is None

    def test_get_failure_reason_with_message(self):
        """Test get_failure_reason method with message attribute."""
        xml_content = """
        <testcase name="test_example">
            <failure message="AssertionError: test failed">Details</failure>
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)

        result = parser.get_failure_reason()
        assert result == "AssertionError: test failed"

    def test_get_failure_reason_multiline_message(self):
        """Test get_failure_reason method with multiline message."""
        xml_content = """
        <testcase name="test_example">
            <failure message="First line
Second line
Third line">Details</failure>
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)

        result = parser.get_failure_reason()
        assert result == "First line"

    @patch('qa_analytics_insights.parser.logger')
    def test_get_failure_reason_no_message(self, mock_logger):
        """Test get_failure_reason method when no message attribute."""
        xml_content = """
        <testcase name="test_example">
            <failure>Details</failure>
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)

        result = parser.get_failure_reason()
        assert result is None
        mock_logger.debug.assert_called()

    def test_get_skipped_reason_with_message(self):
        """Test get_skipped_reason method with message attribute."""
        xml_content = """
        <testcase name="test_example">
            <skipped message="Not applicable">Details</skipped>
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)

        result = parser.get_skipped_reason()
        assert result == "Not applicable"

    @patch('qa_analytics_insights.parser.logger')
    def test_get_skipped_reason_no_message(self, mock_logger):
        """Test get_skipped_reason method when no message attribute."""
        xml_content = """
        <testcase name="test_example">
            <skipped>Details</skipped>
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)

        result = parser.get_skipped_reason()
        assert result is None
        mock_logger.debug.assert_called()

    def test_get_timestamp_from_timestamp_tag(self):
        """Test get_timestamp method from timestamp tag."""
        xml_content = """
        <testcase name="test_example">
            <timestamp>2023-01-01T00:00:00</timestamp>
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)

        result = parser.get_timestamp()
        assert result == "2023-01-01T00:00:00"

    def test_get_timestamp_from_system_out(self):
        """Test get_timestamp method from system-out tag."""
        xml_content = """
        <testcase name="test_example">
            <system-out>20230101 12:34:56 - Some output</system-out>
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)

        result = parser.get_timestamp()
        assert result == "20230101 12:34:56"

    @patch('qa_analytics_insights.parser.logger')
    def test_get_timestamp_not_found(self, mock_logger):
        """Test get_timestamp method when timestamp not found."""
        xml_content = """
        <testcase name="test_example">
            <system-out>Some output without timestamp</system-out>
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)

        result = parser.get_timestamp()
        assert result is None
        mock_logger.debug.assert_called()

    def test_get_system_out(self):
        """Test get_system_out method."""
        xml_content = """
        <testcase name="test_example">
            <system-out>Console output here</system-out>
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)

        result = parser.get_system_out()
        assert result == "Console output here"

    @patch('qa_analytics_insights.parser.logger')
    def test_get_system_out_not_found(self, mock_logger):
        """Test get_system_out method when system-out not found."""
        xml_content = """
        <testcase name="test_example">
        </testcase>
        """
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)

        result = parser.get_system_out()
        assert result is None
        mock_logger.debug.assert_called()
