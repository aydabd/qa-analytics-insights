"""Copyright (c) 2023, Aydin Abdi.

Unit tests for XMLTagFinder class.
"""
from xml.etree import ElementTree as ET

import pytest

from qa_analytics_insights.xml_loader import XMLLoader
from qa_analytics_insights.xml_tag_finder import XMLTagFinder


@pytest.fixture
def xml_loader() -> XMLLoader:
    """Returns XMLLoader object."""
    return XMLLoader("tests/data/pytest_test_result.xml")


@pytest.fixture
def xml_tag_finder(xml_loader: XMLLoader) -> XMLTagFinder:
    """Returns XMLTagFinder object."""
    return XMLTagFinder(xml_loader)


def test_test_cases(xml_tag_finder: XMLTagFinder) -> None:
    """Test test_cases property."""
    assert isinstance(xml_tag_finder.test_cases, list)
    assert len(xml_tag_finder.test_cases) == 2
    assert all(isinstance(tag, ET.Element) for tag in xml_tag_finder.test_cases)


def test_suite(xml_tag_finder: XMLTagFinder) -> None:
    """Test suite property."""
    assert isinstance(xml_tag_finder.suite, ET.Element)
    assert xml_tag_finder.suite.tag == "testsuite"


def test_suite_property(xml_tag_finder: XMLTagFinder) -> None:
    """Test suite property."""
    assert xml_tag_finder.suite == xml_tag_finder.root.find("testsuite")
