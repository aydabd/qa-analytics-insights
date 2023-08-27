"""Copyright (c) 2023, Aydin Abdi.

Command line interface for the qa-analytics-insights package.
"""
import argparse
import sys
from typing import List, Optional  # noqa: F401

from loguru import logger

from qa_analytics_insights import __version__
from qa_analytics_insights.log import (
    default_logging,
    log_execution_time,
    verbose_logging,
)
from qa_analytics_insights.result_analyzer import ResultAnalyzer
from qa_analytics_insights.result_visualizer import ParallelResultVisualizer


class ArgsParser:
    """Class for handling command line arguments."""

    def __init__(self) -> None:
        """Initialize the ArgsParser class."""
        self._parser = None  # type: Optional[argparse.ArgumentParser]
        self._args = None  # type: Optional[argparse.Namespace]

    def add_arguments(self) -> argparse.ArgumentParser:
        """Add command line arguments."""
        parser = argparse.ArgumentParser(
            prog="qa-analytics-insights",
            usage="%(prog)s -f <path/to/files> [options]",
            description="Analyze test reports and generate visualizations.",
            epilog=("Documentation: 'https://qa-analytics-insights.readthedocs.io'."),
        )

        parser.add_argument(
            "-f",
            "--file",
            dest="file_path",
            type=str,
            required=True,
            help="Path to directory or file containing the test results.",
        )
        parser.add_argument(
            "-o",
            "--output",
            dest="output",
            type=str,
            default="test_results_visualization",
            help="Path to the output directory.",
        )
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=__version__,
            help="Show the version of the program.",
        )
        parser.add_argument(
            "-vv",
            "--verbose",
            action="store_true",
            dest="verbose",
            help="Enable verbose logging.",
        )
        return parser

    @property
    def parser(self) -> argparse.ArgumentParser:
        """Return the parser object.

        Returns:
            ArgumentParser object.
        """
        if not self._parser:
            self._parser = self.add_arguments()
        return self._parser

    @property
    def args(self) -> argparse.Namespace:
        """Return the parsed arguments.

        Returns:
            Namespace object.
        """
        if not self._args:
            self._args = self.parser.parse_args()
        return self._args

    def help(self) -> None:
        """Print help message."""
        self.parser.print_help()

    def usage(self) -> None:
        """Print usage message."""
        self.parser.print_usage()


class Cli:
    """Class for handling command line interface."""

    def __init__(self) -> None:
        """Initialize the cli class."""
        self.args_parser = ArgsParser()
        self.args = self.args_parser.args

    def run(self, file_path: str, output: str = "test_results_visualization") -> None:
        """Main execution method."""
        test_result_analyzer = ResultAnalyzer(file_path)
        slowest_test_classes = test_result_analyzer.get_slowest_test_classes()
        test_suites = test_result_analyzer.suites
        parallel_test_result = ParallelResultVisualizer(test_suites)
        parallel_test_result.generate_html_plots(output, slowest_test_classes)

    def cli_main(self, args: Optional[List[str]] = None) -> None:
        """Main method for the command line interface.

        Args:
            args: Command line arguments.
        """
        if args is None:
            args = sys.argv[1:]
        if not args:
            self.args_parser.usage()
            return None
        self.args = self.args_parser.parser.parse_args(args)
        if self.args.verbose:
            verbose_logging()
            logger.info("Log level set to DEBUG.")
        else:
            default_logging()
            logger.info("Log level set to INFO.")
        if self.args.file_path is None:
            self.args_parser.help()
            return None
        logger.info("Starting for creating the visualization...")
        logger
        self.run(self.args.file_path, self.args.output)
        logger.info("Visualization created successfully.")


@log_execution_time
def main(args: Optional[List[str]] = None) -> None:
    """Main method for the command line interface.

    Args:
        args: Command line arguments.
    """
    cli = Cli()
    cli.cli_main(args=args)


if __name__ == "__main__":
    """Entry point."""
    main()
