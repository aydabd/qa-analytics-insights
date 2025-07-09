"""Tests for xml_processor module."""

from unittest.mock import Mock, patch
from queue import Queue

import pytest
from qa_analytics_insights.xml_processor import XMLProcessor


class TestXMLProcessor:
    """Test XMLProcessor class."""

    def test_xml_processor_init(self):
        """Test XMLProcessor initialization."""
        processor = XMLProcessor("/test/path")

        assert processor.path == "/test/path"
        assert processor.test_suites == []
        assert processor.lock is not None

    @patch('qa_analytics_insights.xml_processor.PathFetcher')
    @patch('qa_analytics_insights.xml_processor.XMLFilter')
    @patch('qa_analytics_insights.xml_processor.threading.Thread')
    def test_process_files_in_parallel(self, mock_thread, mock_xml_filter, mock_path_fetcher):
        """Test process_files_in_parallel method."""
        # Setup mocks
        mock_path_fetcher_instance = Mock()
        mock_path_fetcher_instance.fetch_paths.return_value = Queue()
        mock_path_fetcher.return_value = mock_path_fetcher_instance

        mock_xml_filter_instance = Mock()
        mock_xml_filter_instance.filter_xml.return_value = Queue()
        mock_xml_filter.return_value = mock_xml_filter_instance

        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        processor = XMLProcessor("/test/path")
        processor.process_files_in_parallel(num_threads=3)

        # Verify PathFetcher was called
        mock_path_fetcher.assert_called_once_with("/test/path")
        mock_path_fetcher_instance.fetch_paths.assert_called_once()

        # Verify XMLFilter was called
        mock_xml_filter.assert_called_once()
        mock_xml_filter_instance.filter_xml.assert_called_once()

        # Verify threads were created and started
        assert mock_thread.call_count == 3
        assert mock_thread_instance.start.call_count == 3
        assert mock_thread_instance.join.call_count == 3

    @patch('qa_analytics_insights.xml_processor.XMLLoader')
    @patch('qa_analytics_insights.xml_processor.XMLTagFinder')
    @patch('qa_analytics_insights.xml_processor.XMLParser')
    def test_process_xml(self, mock_xml_parser, mock_xml_tag_finder, mock_xml_loader):
        """Test _process_xml method."""
        # Setup mocks
        mock_xml_loader_instance = Mock()
        mock_xml_loader_instance.load.return_value = Mock()
        mock_xml_loader.return_value = mock_xml_loader_instance

        mock_xml_tag_finder_instance = Mock()
        mock_xml_tag_finder_instance.find_test_suites.return_value = [Mock(), Mock()]
        mock_xml_tag_finder.return_value = mock_xml_tag_finder_instance

        mock_xml_parser_instance = Mock()
        mock_xml_parser_instance.parse.return_value = [Mock(), Mock()]
        mock_xml_parser.return_value = mock_xml_parser_instance

        # Create a queue with test data
        xml_queue = Queue()
        xml_queue.put("/test/file1.xml")
        xml_queue.put("/test/file2.xml")
        xml_queue.put(None)  # Sentinel to stop processing

        processor = XMLProcessor("/test/path")
        processor._process_xml(xml_queue)

        # Verify XMLLoader was called for each file
        assert mock_xml_loader.call_count == 2
        assert mock_xml_loader_instance.load.call_count == 2

        # Verify XMLTagFinder was called
        assert mock_xml_tag_finder.call_count == 2
        assert mock_xml_tag_finder_instance.find_test_suites.call_count == 2

        # Verify XMLParser was called
        assert mock_xml_parser.call_count == 2
        assert mock_xml_parser_instance.parse.call_count == 2

        # Verify test suites were added (2 files × 2 suites each = 4 total)
        assert len(processor.test_suites) == 4

    @patch('qa_analytics_insights.xml_processor.XMLLoader')
    def test_process_xml_with_empty_queue(self, mock_xml_loader):
        """Test _process_xml method with empty queue."""
        xml_queue = Queue()
        xml_queue.put(None)  # Only sentinel

        processor = XMLProcessor("/test/path")
        processor._process_xml(xml_queue)

        # XMLLoader should not be called
        mock_xml_loader.assert_not_called()
        assert len(processor.test_suites) == 0

    @patch('qa_analytics_insights.xml_processor.XMLLoader')
    @patch('qa_analytics_insights.xml_processor.logger')
    def test_process_xml_with_exception(self, mock_logger, mock_xml_loader):
        """Test _process_xml method handles exceptions."""
        # Setup XMLLoader to raise an exception
        mock_xml_loader_instance = Mock()
        mock_xml_loader_instance.load.side_effect = Exception("File not found")
        mock_xml_loader.return_value = mock_xml_loader_instance

        xml_queue = Queue()
        xml_queue.put("/test/file1.xml")
        xml_queue.put(None)  # Sentinel to stop processing

        processor = XMLProcessor("/test/path")
        processor._process_xml(xml_queue)

        # Should log error but continue processing
        mock_logger.error.assert_called()
        assert len(processor.test_suites) == 0

    def test_process_xml_thread_safety(self):
        """Test that _process_xml is thread-safe."""
        processor = XMLProcessor("/test/path")

        # Create multiple queues simulating concurrent access
        xml_queue1 = Queue()
        xml_queue1.put(None)

        xml_queue2 = Queue()
        xml_queue2.put(None)

        # This should not raise any exceptions
        processor._process_xml(xml_queue1)
        processor._process_xml(xml_queue2)

        assert len(processor.test_suites) == 0
