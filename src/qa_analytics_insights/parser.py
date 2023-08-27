"""Copyright (c) 2023, Aydin Abdi.

This module is responsible for parsing test cases from XML tags.
"""
import re
from typing import Optional
from xml.etree import ElementTree as ET

from loguru import logger

from qa_analytics_insights.data_classes import TestCase, TestSuite


class ParserTestSuite:
    """Responsible for parsing TestSuite objects from XML tags."""

    def __init__(self, test_suite: ET.Element) -> None:
        """Responsible for parsing TestSuite objects from XML tags.

        Args:
            test_suite: XML tag of the test suite.
        """
        self.test_suite = test_suite

    def parse(self) -> TestSuite:
        """Parses the XML tag into TestSuite object.

        Returns:
            TestSuite object.
        """
        suite_name = self.test_suite.attrib.get("name", "")
        suite_tests = int(self.test_suite.attrib.get("tests", 0))
        suite_errors = int(self.test_suite.attrib.get("errors", 0))
        suite_failures = int(self.test_suite.attrib.get("failures", 0))
        suite_skipped = int(
            self.test_suite.attrib.get("skip")
            or self.test_suite.attrib.get("skipped")
            or 0
        )
        suite_execution_time = float(self.test_suite.attrib.get("time", 0))
        suite_timestamp = self.test_suite.attrib.get("timestamp", "")

        test_suite = TestSuite(
            name=suite_name,
            tests=suite_tests,
            errors=suite_errors,
            failures=suite_failures,
            skipped=suite_skipped,
            execution_time=suite_execution_time,
            timestamp=suite_timestamp,
        )

        return test_suite


class ParserTestCase:
    """Responsible for parsing TestCase objects from XML tags."""

    def __init__(self, test_case: ET.Element) -> None:
        """Responsible for parsing TestCase objects from XML tag.

        Args:
            test_case: XML tag of the test case.
        """
        self.test_case = test_case

    def parse(self) -> TestCase:
        """Parses the XML tag into TestCase object.

        Returns:
            TestCase object.
        """
        test_class_name = self.test_case.attrib.get("classname", "")
        if test_class_name:
            test_class_name = test_class_name.split(".")[-1]

        test_module_name = self.test_case.attrib.get("classname", "")
        if test_module_name:
            test_module_name = test_module_name.split(".")[-2]

        test_case_name = self.test_case.attrib.get("name", "")
        test_case_time = float(self.test_case.attrib.get("time", 0))
        test_case_result = self.get_testcase_result()

        failure_reason = None
        error_reason = None
        skipped_reason = None
        if test_case_result == "failed":
            failure_reason = self.get_failure_reason()
        if test_case_result == "error":
            error_reason = self.get_failure_reason(tag="error")

        if test_case_result == "skipped":
            skipped_reason = self.get_skipped_reason()

        system_out = self.get_system_out()
        time_stamp = self.get_timestamp()

        return TestCase(
            name=test_case_name,
            test_module=test_module_name,
            test_class=test_class_name,
            execution_time=test_case_time,
            result=test_case_result,
            timestamp=time_stamp,
            failure_reason=failure_reason,
            error_reason=error_reason,
            skipped_reason=skipped_reason,
            system_out=system_out,
        )

    def get_testcase_result(self) -> str:
        """Parses the test case result from the test case tag.

        Returns:
            Test case result.
        """
        result = "passed"
        if self.test_case.find("failure") is not None:
            result = "failed"
        elif self.test_case.find("skipped") is not None:
            result = "skipped"
        elif self.test_case.find("error") is not None:
            result = "error"
        return result

    def find_tag_attribute(
        self, tag: str, attrib: Optional[str] = None
    ) -> Optional[str]:
        """Find the tag for test case element and return the attribute or text.

        Args:
            tag: Tag to parse.
            attrib: Attribute to parse. If None, the tag text is returned.

        Returns:
            Find the tag and return the attribute or text.
        """
        found_tag = self.test_case.find(tag)
        if found_tag is None:
            return None
        if attrib is not None:
            attrib_text = found_tag.get(attrib)
            return attrib_text
        return found_tag.text

    def get_failure_reason(self, tag: str = "failure") -> Optional[str]:
        """Parse the failure reason from a failure tag.

        Args:
            tag: XML element representing a failure tag. Defaults to "failure".

        Returns:
            Failure reason.
        """
        failure_message = self.find_tag_attribute(tag, "message")
        if not failure_message:
            logger.debug(
                f"{tag.upper()} message not found in {tag} tag. "
                f"Test case: {self.test_case.text}"
            )
            return None
        try:
            # Try to extract the failure reason from the failure message
            split_by_captured_logging = failure_message.strip().split("\n")
            if split_by_captured_logging:
                failure_reason = split_by_captured_logging[0]
                return failure_reason
        except Exception as message_parse_exception:
            logger.warning(
                f"Could not parse {tag} reason from {tag} message."
                f"Exception: {message_parse_exception}"
            )
            logger.warning(f"Test case: {self.test_case.text}")
        return failure_message

    def get_skipped_reason(self, tag: str = "skipped") -> Optional[str]:
        """Parse the skipped reason from a skipped tag.

        Args:
            tag: XML element representing a skipped tag. Defaults to "skipped".

        Returns:
            Skipped reason.
        """
        skipped_message = self.find_tag_attribute(tag, "message")
        if skipped_message:
            return skipped_message

        logger.debug(
            "Skipped message not found in skipped tag. Test case: {test_case.text}"
        )
        return None

    def get_timestamp(self, tag: str = "system-out") -> Optional[str]:
        """Parse the timestamp from a system-out tag or timestamp tag.

        Args:
            tag: XML element representing a system-out tag. Defaults to "system-out".

        Returns:
            Timestamp or None if no timestamp is found.
        """
        # check if any timestamp tag exists
        timestamp_found = self.find_tag_attribute(tag="timestamp")
        if timestamp_found is not None:
            logger.debug(f"Tag timestamp found: {timestamp_found}")
            return timestamp_found
        logger.debug(f"Tag timestamp not found: {timestamp_found}")
        logger.debug(f"Parsing timestamp from {tag} tag...")

        system_out_tag = self.find_tag_attribute(tag)
        # Sometimes the timestamp is in the first line of the system-out tag
        if system_out_tag:
            timestamp_text = system_out_tag.strip().split("\n")[0]
            # Extract timestamp using regex
            # assuming it's in the format YYYYMMDD HH:MM:SS
            timestamp_match = re.match(r"(\d{8} \d{2}:\d{2}:\d{2})", timestamp_text)
            if timestamp_match:
                logger.debug(f"Found timestamp: {timestamp_match.group(0)}")
                return timestamp_match.group(0)

        logger.debug(f"Timestamp not parsed. Unexpected system-out: {system_out_tag}.")
        return None

    def get_system_out(self, tag: str = "system-out") -> Optional[str]:
        """Parse the system out from a system-out tag.

        Args:
            tag: Tag to parse.

        Returns:
            System out or None if no system out is found.
        """
        system_out_tag = self.find_tag_attribute(tag)

        # The system out is the text after the CDATA
        if system_out_tag:
            system_out_text = system_out_tag
            return system_out_text

        logger.debug(
            f"Could not parse system out from system-out tag: {system_out_tag}"
        )
        return None
