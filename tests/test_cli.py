"""Tests for cli module."""

import argparse
import sys
from unittest.mock import Mock, patch

import pytest
from qa_analytics_insights.cli import ArgsParser, Cli, main


class TestArgsParser:
    """Test ArgsParser class."""

    def test_args_parser_init(self):
        """Test ArgsParser initialization."""
        parser = ArgsParser()
        assert parser._parser is None
        assert parser._args is None

    def test_add_arguments(self):
        """Test add_arguments method."""
        parser = ArgsParser()
        arg_parser = parser.add_arguments()
        
        assert isinstance(arg_parser, argparse.ArgumentParser)
        assert arg_parser.prog == "qa-analytics-insights"

    def test_parser_property(self):
        """Test parser property."""
        parser = ArgsParser()
        arg_parser = parser.parser
        
        assert isinstance(arg_parser, argparse.ArgumentParser)
        assert parser._parser is not None

    def test_parser_property_caching(self):
        """Test that parser property caches the result."""
        parser = ArgsParser()
        arg_parser1 = parser.parser
        arg_parser2 = parser.parser
        
        assert arg_parser1 is arg_parser2

    @patch('sys.argv', ['qa-analytics-insights', '-f', '/test/path'])
    def test_args_property(self):
        """Test args property."""
        parser = ArgsParser()
        args = parser.args
        
        assert isinstance(args, argparse.Namespace)
        assert args.file_path == '/test/path'

    def test_help_method(self):
        """Test help method."""
        parser = ArgsParser()
        with patch.object(parser.parser, 'print_help') as mock_help:
            parser.help()
            mock_help.assert_called_once()

    def test_usage_method(self):
        """Test usage method."""
        parser = ArgsParser()
        with patch.object(parser.parser, 'print_usage') as mock_usage:
            parser.usage()
            mock_usage.assert_called_once()

    def test_required_file_argument(self):
        """Test that file argument is required."""
        parser = ArgsParser()
        with pytest.raises(SystemExit):
            parser.parser.parse_args([])

    def test_file_argument_parsing(self):
        """Test file argument parsing."""
        parser = ArgsParser()
        args = parser.parser.parse_args(['-f', '/test/path'])
        assert args.file_path == '/test/path'

    def test_output_argument_parsing(self):
        """Test output argument parsing."""
        parser = ArgsParser()
        args = parser.parser.parse_args(['-f', '/test/path', '-o', '/output/path'])
        assert args.output == '/output/path'

    def test_output_argument_default(self):
        """Test output argument default value."""
        parser = ArgsParser()
        args = parser.parser.parse_args(['-f', '/test/path'])
        assert args.output == 'test_results_visualization'

    def test_verbose_argument_parsing(self):
        """Test verbose argument parsing."""
        parser = ArgsParser()
        args = parser.parser.parse_args(['-f', '/test/path', '-vv'])
        assert args.verbose is True

    def test_verbose_argument_default(self):
        """Test verbose argument default value."""
        parser = ArgsParser()
        args = parser.parser.parse_args(['-f', '/test/path'])
        assert args.verbose is False


class TestCli:
    """Test Cli class."""

    @patch('qa_analytics_insights.cli.ArgsParser')
    def test_cli_init(self, mock_args_parser):
        """Test Cli initialization."""
        mock_args_parser_instance = Mock()
        mock_args_parser_instance.args = Mock()
        mock_args_parser.return_value = mock_args_parser_instance
        
        cli = Cli()
        
        assert cli.args_parser == mock_args_parser_instance
        assert cli.args == mock_args_parser_instance.args

    @patch('qa_analytics_insights.cli.ResultAnalyzer')
    @patch('qa_analytics_insights.cli.ParallelResultVisualizer')
    def test_run_method(self, mock_visualizer, mock_analyzer):
        """Test run method."""
        # Setup mocks
        mock_analyzer_instance = Mock()
        mock_analyzer_instance.get_slowest_test_classes.return_value = ["slow_class"]
        mock_analyzer_instance.suites = ["suite1", "suite2"]
        mock_analyzer.return_value = mock_analyzer_instance
        
        mock_visualizer_instance = Mock()
        mock_visualizer.return_value = mock_visualizer_instance
        
        cli = Cli()
        cli.run("/test/path", "/output/path")
        
        # Verify ResultAnalyzer was called
        mock_analyzer.assert_called_once_with("/test/path")
        mock_analyzer_instance.get_slowest_test_classes.assert_called_once()
        
        # Verify ParallelResultVisualizer was called
        mock_visualizer.assert_called_once_with(["suite1", "suite2"])
        mock_visualizer_instance.generate_html_plots.assert_called_once_with("/output/path", ["slow_class"])

    @patch('qa_analytics_insights.cli.default_logging')
    @patch('qa_analytics_insights.cli.verbose_logging')
    @patch('qa_analytics_insights.cli.logger')
    def test_cli_main_with_verbose(self, mock_logger, mock_verbose_logging, mock_default_logging):
        """Test cli_main method with verbose flag."""
        cli = Cli()
        cli.run = Mock()
        
        # Mock args
        mock_args = Mock()
        mock_args.verbose = True
        mock_args.file_path = "/test/path"
        mock_args.output = "/output/path"
        
        cli.args_parser = Mock()
        cli.args_parser.parser.parse_args.return_value = mock_args
        
        cli.cli_main(['-f', '/test/path', '-vv'])
        
        mock_verbose_logging.assert_called_once()
        mock_logger.info.assert_called()
        cli.run.assert_called_once_with("/test/path", "/output/path")

    @patch('qa_analytics_insights.cli.default_logging')
    @patch('qa_analytics_insights.cli.logger')
    def test_cli_main_without_verbose(self, mock_logger, mock_default_logging):
        """Test cli_main method without verbose flag."""
        cli = Cli()
        cli.run = Mock()
        
        # Mock args
        mock_args = Mock()
        mock_args.verbose = False
        mock_args.file_path = "/test/path"
        mock_args.output = "/output/path"
        
        cli.args_parser = Mock()
        cli.args_parser.parser.parse_args.return_value = mock_args
        
        cli.cli_main(['-f', '/test/path'])
        
        mock_default_logging.assert_called_once()
        cli.run.assert_called_once_with("/test/path", "/output/path")

    def test_cli_main_no_args(self):
        """Test cli_main method with no arguments."""
        cli = Cli()
        cli.args_parser = Mock()
        
        result = cli.cli_main([])
        
        cli.args_parser.usage.assert_called_once()
        assert result is None

    def test_cli_main_no_file_path(self):
        """Test cli_main method with no file path."""
        cli = Cli()
        cli.args_parser = Mock()
        
        # Mock args with no file_path
        mock_args = Mock()
        mock_args.file_path = None
        cli.args_parser.parser.parse_args.return_value = mock_args
        
        result = cli.cli_main(['-vv'])
        
        cli.args_parser.help.assert_called_once()
        assert result is None


@patch('qa_analytics_insights.cli.Cli')
def test_main_function(mock_cli):
    """Test main function."""
    mock_cli_instance = Mock()
    mock_cli.return_value = mock_cli_instance
    
    main(['-f', '/test/path'])
    
    mock_cli.assert_called_once()
    mock_cli_instance.cli_main.assert_called_once_with(args=['-f', '/test/path'])


@patch('qa_analytics_insights.cli.main')
def test_main_entry_point(mock_main):
    """Test main entry point when module is run directly."""
    # This would test the if __name__ == "__main__" block
    # Since we can't easily test that directly, we just verify main can be called
    main()
    mock_main.assert_called_once_with()