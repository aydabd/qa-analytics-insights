"""Tests for parser module."""

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
        with patch.object(parser, '_parse_failure_reason', side_effect=Exception("parse error")):
            test_case = parser.parse()
            
            # Should log warning about parsing failure
            assert mock_logger.warning.called