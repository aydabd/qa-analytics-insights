"""Unittests for the xml_filter module."""
from pathlib import Path
from queue import Queue

from qa_analytics_insights.xml_filter import XMLFilter


def test_filter_xml() -> None:
    """
    Test the filter_xml method of XMLFilter.

    Args:
        xml_filter_instance (XMLFilter): An instance of XMLFilter.
    """
    path_queue = Queue()
    path_queue.put(Path("tests/data/nosetests_test_result.xml"))
    path_queue.put(Path("tests/data/text.txt"))
    xml_filter = XMLFilter(path_queue)
    xml_queue = xml_filter.filter_xml()
    assert xml_queue.get() == Path("tests/data/nosetests_test_result.xml")
    assert xml_queue.empty()
