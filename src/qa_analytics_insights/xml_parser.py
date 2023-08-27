"""Copyright (c) 2023, Aydin Abdi.

This module is responsible for parsing XML files into TestSuite objects.
"""
from collections import defaultdict
from typing import List  # noqa: F401
from xml.etree import ElementTree as ET  # noqa: F401

from loguru import logger

from qa_analytics_insights.data_classes import TestClass, TestSuite
from qa_analytics_insights.parser import ParserTestCase, ParserTestSuite
from qa_analytics_insights.xml_tag_finder import XMLTagFinder


class XMLParser:
    """Responsible for parsing XML files into TestClass and TestCase objects."""

    def __init__(self, xml_tag_finder: XMLTagFinder) -> None:
        """Responsible for parsing XML files into TestClass and TestCase objects.

        Args:
            xml_tag_finder: XMLTagFinder object.
        """
        self.xml_tag_finder = xml_tag_finder
        self.root = self.xml_tag_finder.root  # type: ET.Element
        self.xml_path = self.xml_tag_finder.xml_loader.xml_path  # type: str
        self.test_case_tags = self.xml_tag_finder.test_cases  # type: List[ET.Element]
        self.suite_tag = self.xml_tag_finder.suite  # type: ET.Element
        self.suite_parser = ParserTestSuite(self.suite_tag)  # type: ParserTestSuite

    def parse(self) -> TestSuite:
        """Parses the XML file into TestClass and TestCase objects.

        This method parses test cases and groups them by their class name.
        If a test case has no class name,it will be added to the
        ungrouped_test_cases list.

        Returns:
            TestSuite object.
        """
        ungrouped_test_cases = []
        classwise_test_cases = defaultdict(list)

        # Creating test cases and grouping them by classname
        for testcase in self.test_case_tags:
            test_case_parser = ParserTestCase(testcase)
            test_case = test_case_parser.parse()
            if not test_case.test_class or test_case.test_class is None:
                logger.debug(f"Test case {test_case.name} has no test class.")
                ungrouped_test_cases.append(test_case)
            else:
                classwise_test_cases[test_case.test_class].append(test_case)

        # Creating TestClass objects from the grouped test cases
        test_classes = [
            TestClass(name=classname, test_cases=test_cases)
            for classname, test_cases in classwise_test_cases.items()
        ]

        # Creating TestSuite object
        test_suite = self.suite_parser.parse()
        test_suite.test_classes = test_classes
        test_suite.test_cases = ungrouped_test_cases

        return test_suite
