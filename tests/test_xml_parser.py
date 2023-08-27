"""Copyright (c) 2023, Aydin Abdi.

Unit-tests for the xml_parser module.
"""
from qa_analytics_insights.xml_loader import XMLLoader
from qa_analytics_insights.xml_parser import XMLParser
from qa_analytics_insights.xml_tag_finder import XMLTagFinder

nosetests_xml = "tests/data/nosetests_test_result.xml"
pytests_xml = "tests/data/pytest_test_result.xml"
invalid_file = "tests/data/text.txt"


def test_parse_with_pytest_xml():
    """Tests the `parse` method for pytest XML files."""
    xml_loader = XMLLoader(pytests_xml)
    xml_tag_finder = XMLTagFinder(xml_loader)
    parser = XMLParser(xml_tag_finder)
    test_suite = parser.parse()

    assert test_suite.name == "qa-analytics-insights"
    assert test_suite.tests == 3
    assert test_suite.errors == 0
    assert test_suite.failures == 1
    assert test_suite.skipped == 1
    assert len(test_suite.test_classes) == 2
    assert len(test_suite.test_cases) == 0
    assert test_suite.passed == 1


def test_parse_with_nosetests_xml():
    """Tests the `parse` method for nosetests XML files."""
    xml_loader = XMLLoader(nosetests_xml)
    xml_tag_finder = XMLTagFinder(xml_loader)
    parser = XMLParser(xml_tag_finder)
    test_suite = parser.parse()

    assert test_suite.name == "nosetests"
    assert test_suite.tests == 6
    assert test_suite.errors == 1
    assert test_suite.failures == 1
    assert test_suite.skipped == 1
    assert len(test_suite.test_classes) == 5
    assert len(test_suite.test_cases) == 1
    assert test_suite.passed == 3
