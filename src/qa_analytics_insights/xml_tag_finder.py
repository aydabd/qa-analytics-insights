"""Copyright (c) 2023, Aydin Abdi.

This module is responsible for finding XML tags in XML files.
"""
from typing import List, Optional  # noqa F401
from xml.etree import ElementTree as ET

from qa_analytics_insights.xml_loader import XMLLoader


class XMLTagFinder:
    """Responsible for finding XML tags in XML files."""

    def __init__(self, xml_loader: XMLLoader) -> None:
        """Responsible for finding XML tags in XML files.

        Args:
            xml_loader: XMLLoader object.
        """
        self.xml_loader = xml_loader
        self.root = self.xml_loader.root  # type: ET.Element
        self._test_cases = []  # type: List[ET.Element]
        self._suite = None  # type: Optional[ET.Element]

    @property
    def test_cases(self) -> List[ET.Element]:
        """Returns all the testcase tags in the XML file.

        Returns:
            List of testcase tags.
        """
        if not self._test_cases:
            self._test_cases = self.root.findall(".//testcase")
        return self._test_cases

    @property
    def suite(self) -> ET.Element:
        """Returns the suite element.

        This method returns the testsuite element if it exists.
        If the testsuite element does not exist, it returns the root element.

        Returns:
            Suite element.
        """
        if self._suite is None:
            self._suite = self.root.find("testsuite") or self.root
        return self._suite
