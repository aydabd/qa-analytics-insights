"""Copyright (c) 2023, Aydin Abdi.

This module is responsible for visualizing the results of the parsed TestClass objects.
"""
from __future__ import annotations

import base64
import math
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import List, Optional

import matplotlib
from loguru import logger
from matplotlib import pyplot as plt

from qa_analytics_insights.data_classes import TestCase, TestClass, TestSuite

# Don't use GUI backend for matplotlib to avoid errors when running on a server.
matplotlib.use('Agg')


class ResultVisualizer:
    """Class for visualizing test results."""

    def __init__(
        self,
        test_suites: Optional[List[TestSuite]] = None,
    ) -> None:
        """Initialize the TestResultVisualizer class.

        Args:
            test_suites: List of TestSuite objects.
        """
        self.test_suites = test_suites
        self._test_classes = []  # type: List[TestClass]
        self._test_cases = []  # type: List[TestCase]
        self.plot = plt

    @property
    def test_classes(self) -> List[TestClass]:
        """Return the test classes.

        Returns:
            List of TestClass objects.
        """
        if not self._test_classes:
            if not self.test_suites or self.test_suites is None:
                logger.warning("No test suites found.")
                return []
            for test_suite in self.test_suites:
                self._test_classes.extend(test_suite.test_classes)
        return self._test_classes

    @property
    def test_cases(self) -> List[TestCase]:
        """Return the test cases.

        Returns:
            List of TestCase objects.
        """
        if not self._test_cases:
            if not self.test_suites or self.test_suites is None:
                logger.warning("No test suites found.")
                return []
            for test_suite in self.test_suites:
                self._test_cases.extend(test_suite.test_cases)
            for test_class in self.test_classes:
                self._test_cases.extend(test_class.test_cases)
        return self._test_cases

    def plot_pie_charts_test_classes(self) -> Optional[plt.Figure]:
        """Plot pie charts for each test class.

        Returns:
            Figure containing the pie charts.
        """
        logger.info("Plotting pie charts for test results.")
        if not self.test_classes:
            logger.warning("No test classes found.")
            return None

        num_test_classes = len(self.test_classes)
        num_rows = math.ceil(math.sqrt(num_test_classes))
        num_cols = math.ceil(num_test_classes / num_rows)
        pix_size_x = len(self.test_classes) * 2
        pix_size_y = len(self.test_classes) / 2

        pie_charts, axes = self.plot.subplots(
            num_rows, num_cols, figsize=(pix_size_x, pix_size_y), clear=True
        )
        axes = axes.flatten()

        for ax, test_class in zip(axes, self.test_classes):
            statuses = {"skipped": 0, "failed": 0, "passed": 0, "error": 0}
            colors = {
                "skipped": "gray",
                "failed": "red",
                "passed": "green",
                "error": "orange",
            }
            for test_case in test_class.test_cases:
                statuses[test_case.result] += 1
            labels = list(statuses.keys())
            sizes = [statuses[key] for key in labels]
            labels_with_counts = [
                f"{label} ({count})" for label, count in zip(labels, sizes)
            ]
            ax.pie(
                sizes,
                autopct='%1.1f%%',
                startangle=180,
                colors=[colors[key] for key in labels],
                textprops={'fontsize': 6},
            )
            ax.axis('equal')
            ax.set_title(f"{test_class.name}")
            ax.legend(labels_with_counts, loc='upper right', fontsize=6)

        # Remove unused subplots
        for i in range(num_test_classes, num_rows * num_cols):
            pie_charts.delaxes(axes[i])

        return pie_charts

    def plot_failed_test_cases_table(self) -> Optional[plt.Figure]:
        """Plot a table of failed/error test cases.

        returns:
            The figure for failed/error test cases table.
        """
        logger.info("Creating failed/error test cases table.")
        all_failed_tests = []

        if self.test_cases:
            for testcase in self.test_cases:
                if testcase.result == "failed" or testcase.result == "error":
                    all_failed_tests.append(
                        (
                            testcase.test_class or "N/A",
                            testcase.name,
                            testcase.failure_reason or testcase.error_reason,
                        )
                    )

        if not all_failed_tests:
            logger.warning("No failed test cases found.")
            return None

        lenght_failed_tests = len(all_failed_tests)
        pixels_per_row = lenght_failed_tests * 2
        pixels_per_column = lenght_failed_tests / 4

        failed_test_cases_table, axes = self.plot.subplots(
            figsize=(pixels_per_row, pixels_per_column)
        )
        axes.axis('tight')
        axes.axis('off')
        columns = ("Test Class", "Test Name", "Failure Reason")
        table = axes.table(
            cellText=all_failed_tests,
            colLabels=columns,
            cellLoc='left',
            loc='left',
            colColours=['#DDEBF7'] * len(columns),
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)

        # Loop over cells to adjust the cell borders and wrap text for better formatting
        for _, cell in table.get_celld().items():
            cell.set_edgecolor("black")
            cell.set_linewidth(0.5)
            text = cell.get_text().get_text()
            cell.set_text_props(wrap=True)
            cell._text.set_text(text)

        # Adjust layout to make sure everything fits
        table.auto_set_column_width(col=list(range(len(columns))))
        table.scale(1.5, 1.5)  # Increase the size of cells to fit text

        return failed_test_cases_table

    def plot_skipped_test_cases_table(self) -> Optional[plt.Figure]:
        """Plot a table of skipped test cases.

        returns:
            The figure for skipped test cases table.
        """
        logger.info("Creating skipped test cases table.")
        all_skipped_tests = []
        # if self.test_classes:
        #     for test_class in self.test_classes:
        #         all_skipped_tests.extend(
        #             [
        #                 (test_class.name, tc.name, tc.skipped_reason)
        #                 for tc in test_class.skipped_test_cases
        #             ]
        #         )

        if self.test_cases:
            for test_case in self.test_cases:
                if test_case.result == "skipped":
                    all_skipped_tests.append(
                        (
                            test_case.test_class or "N/A",
                            test_case.name,
                            test_case.skipped_reason,
                        )
                    )

        if not all_skipped_tests:
            logger.warning("No skipped test cases found.")
            return None

        lenght_skipped_tests = len(all_skipped_tests)
        pixels_per_row = lenght_skipped_tests * 2
        pixels_per_column = lenght_skipped_tests / 4

        skipped_test_cases_table, axes = self.plot.subplots(
            figsize=(pixels_per_row, pixels_per_column)
        )
        axes.axis('tight')
        axes.axis('off')
        columns = ("Test Class", "Test Name", "Skipped Reason")
        table = axes.table(
            cellText=all_skipped_tests,
            colLabels=columns,
            cellLoc='left',
            loc='left',
            colColours=['#DDEBF7'] * len(columns),
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)

        # Loop over cells to adjust the cell borders and wrap text for better formatting
        for _, cell in table.get_celld().items():
            cell.set_edgecolor("black")
            cell.set_linewidth(0.5)
            text = cell.get_text().get_text()
            cell.set_text_props(wrap=True)
            cell._text.set_text(text)

        # Adjust layout to make sure everything fits
        table.auto_set_column_width(col=list(range(len(columns))))
        table.scale(1.5, 1.5)  # Increase the size of cells to fit text

        return skipped_test_cases_table

    def plot_top_slowest_test_classes_pie_bar_chart(
        self, slowest_test_classes: Optional[List[TestClass]] = None
    ) -> Optional[plt.Figure]:
        """Plot a pie bar chart of the top slowest test classes.

        Args:
            slowest_test_classes: List of the slowest test classes.

        Returns:
            The figure for the top slowest test classes pie bar chart.
        """
        logger.info("Creating top slowest test classes pie bar chart.")
        if not slowest_test_classes or slowest_test_classes is None:
            logger.warning("No slowest test classes found.")
            return None
        labels = [test_class.name for test_class in slowest_test_classes]
        sizes = [test_class.execution_time for test_class in slowest_test_classes]

        top_slowest_test_classes_pie_bar_chart, axes = self.plot.subplots(
            figsize=(20, len(labels)), clear=True
        )
        axes.bar(labels, sizes, color="green")
        axes.set_ylabel("Execution Time (seconds)", fontsize=12)
        axes.set_xlabel("Test Class", fontsize=12)

        return top_slowest_test_classes_pie_bar_chart

    @staticmethod
    def figure_to_base64(figure: plt.Figure) -> str:
        """Convert a Matplotlib figure to a base64 string.

        Args:
            figure: The figure to convert.

        Returns:
            The base64 encoded string representation of the figure.
        """
        img = BytesIO()
        figure.savefig(img, format="svg", bbox_inches="tight")
        img.seek(0)
        return base64.b64encode(img.read()).decode()

    def build_subplots_pie_chart_test_classes_results(self) -> Optional[str]:
        """Plot the results of the parsed TestClass objects.

        Returns:
            The base64 encoded string representation of the figure.
        """
        # Create the pie chart figure
        pie_charts = self.plot_pie_charts_test_classes()
        if pie_charts is None:
            logger.debug("No test classes found.")
            return None
        return self.figure_to_base64(pie_charts)

    def build_subplots_failed_table(self) -> Optional[str]:
        """Plot a table of failed test cases.

        Returns:
            The base64 encoded string representation of the figure.
        """
        failed_test_cases_table = self.plot_failed_test_cases_table()
        if failed_test_cases_table is None:
            logger.debug("No failed test cases found.")
            return None
        return self.figure_to_base64(failed_test_cases_table)

    def build_subplots_skipped_table(self) -> Optional[str]:
        """Plot a table of skipped test cases.

        Returns:
            The base64 encoded string representation of the figure.
        """
        skipped_test_cases_table = self.plot_skipped_test_cases_table()
        if skipped_test_cases_table is None:
            logger.debug("No skipped test cases found.")
            return None
        return self.figure_to_base64(skipped_test_cases_table)

    def build_subplots_top_slowest_test_classes(
        self, slowest_test_classes: List[TestClass]
    ) -> Optional[str]:
        """Plot a pie bar chart of the top slowest test classes.

        Args:
            slowest_test_classes: List of the slowest test classes.

        Returns:
            The base64 encoded string representation of the figure.
        """
        slowest_tests_bar_chart = self.plot_top_slowest_test_classes_pie_bar_chart(
            slowest_test_classes
        )
        if slowest_tests_bar_chart is None:
            logger.debug("No slowest test classes found.")
            return None
        return self.figure_to_base64(slowest_tests_bar_chart)

    def plot_test_suites_summary_table(self) -> Optional[plt.Figure]:
        """Plot a table of test suites summary.

        Returns:
            The figure for test suites summary table.
        """
        logger.info("Creating test suites summary table.")
        test_suites_summary = []
        if self.test_suites:
            for test_suite in self.test_suites:
                test_suites_summary.append(
                    (
                        test_suite.name,
                        test_suite.passed,
                        test_suite.failures,
                        test_suite.skipped,
                        test_suite.errors,
                        test_suite.execution_time,
                    )
                )

        if not test_suites_summary:
            logger.warning("No test suites found.")
            return None

        lenght_test_suites_summary = len(test_suites_summary)
        pixels_per_row = lenght_test_suites_summary * 2
        pixels_per_column = lenght_test_suites_summary / 4

        test_suites_summary_table, axes = self.plot.subplots(
            figsize=(pixels_per_row, pixels_per_column)
        )
        axes.axis('tight')
        axes.axis('off')
        columns = ("Test Suite", "Passed", "Failed", "Skipped", "Errors", "Time")
        table = axes.table(
            cellText=test_suites_summary,
            colLabels=columns,
            cellLoc='left',
            loc='left',
            colColours=['#DDEBF7'] * len(columns),
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)

        # Loop over cells to adjust the cell borders and wrap text for better formatting
        for _, cell in table.get_celld().items():
            cell.set_edgecolor("black")
            cell.set_linewidth(0.5)
            text = cell.get_text().get_text()
            cell.set_text_props(wrap=True)
            cell._text.set_text(text)

        # Adjust layout to make sure everything fits
        table.auto_set_column_width(col=list(range(len(columns))))
        table.scale(1.5, 1.5)

        return test_suites_summary_table

    def build_subplots_test_suites_summary_table(self) -> Optional[str]:
        """Plot a table of test suites summary.

        Returns:
            The base64 encoded string representation of the figure.
        """
        test_suites_summary_table = self.plot_test_suites_summary_table()
        if test_suites_summary_table is None:
            logger.debug("No test suites found.")
            return None
        return self.figure_to_base64(test_suites_summary_table)

    @staticmethod
    def generate_html_report_to_file(
        output: str,
        pie_charts: Optional[str] = None,
        failed_table: Optional[str] = None,
        skipped_table: Optional[str] = None,
        summary_table: Optional[str] = None,
        slowest_classes: Optional[str] = None,
    ) -> None:
        """Generate an HTML report of the test results.

        Args:
            pie_charts: Base64 string representing the pie charts.
            failed_table: Base64 string representing the failed test cases table.
            skipped_table: Base64 string representing the skipped test cases table.
            summary_table: Base64 string representing the test suites summary table.
            slowest_classes: Base64 string representing the top slowest test classes.
            output: Output file name.
        """
        logger.info("Generating HTML report...")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Results Visualization</title>
        </head>
        <body>
            <h1>Generated Test Result({timestamp})</h1>
            <h2>Test Suites Summary</h2>
            <img
                src="data:image/svg+xml;base64,{summary_table}"
                alt="Test Suites Summary Table">
            <h2>Test Results Pie Charts Based on Test Classes</h2>
            <img
                src="data:image/svg+xml;base64,{pie_charts}"
                alt="Test Results Pie Charts">
            <h2>Failed Test Cases</h2>
            <img
                src="data:image/svg+xml;base64,{failed_table}"
                alt="Failed Test Cases Table">
            <h2>Top Slowest Test Classes</h2>
            <img
                src="data:image/svg+xml;base64,{slowest_classes}"
                alt="Top Slowest Test Classes Pie Bar Chart">
            <h2>Skipped Test Cases</h2>
            <img src="data:image/svg+xml;base64,{skipped_table}"
                alt="Skipped Test Cases Table">
        </body>
        </html>
        """

        # Save the HTML content to a file
        html_file_path = f"{output}.html"
        with open(html_file_path, "w") as f:
            f.write(html_content)
        logger.info(f"HTML report saved to: {Path(html_file_path).absolute()}")

    def run(
        self,
        output: str = "test_results_visualization",
        pie_charts: Optional[plt.Figure] = None,
        failed_table: Optional[plt.Figure] = None,
        skipped_table: Optional[plt.Figure] = None,
        summary_table: Optional[plt.Figure] = None,
        slowest_classes: Optional[List[TestClass]] = None,
    ) -> None:
        """Main execution method.

        Args:
            output: Output file name.
            pie_charts: Figure containing the pie charts.
            failed_table: Figure containing the failed test cases table.
            skipped_table: Figure containing the skipped test cases table.
            slowest_classes: List of the slowest test classes.
            summary_table: Figure containing the test suites summary table.
        """
        if pie_charts:
            pie_charts = self.build_subplots_pie_chart_test_classes_results()
        if failed_table:
            failed_table = self.build_subplots_failed_table()
        if skipped_table:
            skipped_table = self.build_subplots_skipped_table()
        if summary_table:
            summary_table = self.build_subplots_test_suites_summary_table()
        if slowest_classes:
            slowest_test_classes = self.build_subplots_top_slowest_test_classes(
                slowest_classes
            )

        self.generate_html_report_to_file(
            output,
            pie_charts,
            failed_table,
            skipped_table,
            summary_table,
            slowest_test_classes,
        )


class ParallelResultVisualizer(ResultVisualizer):
    """Class to visualize the results of the parsed TestClass objects in parallel."""

    def __init__(
        self,
        test_suites: Optional[List[TestSuite]] = None,
    ) -> None:
        """Initialize the ParallelTestResultVisualizer class.

        Args:
            test_classes: List of TestClass objects.
        """
        super().__init__(test_suites)

    def generate_html_plots(
        self,
        output: str,
        slowest_test_classes: Optional[List[TestClass]] = None,
    ) -> None:
        """Main execution method.

        Args:
            output: Output file name.
            slowest_test_classes: List of the slowest test classes.
        """
        slowest_classes_base64 = None
        # Use ThreadPoolExecutor to run plot generation in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            pie_chart_future = executor.submit(
                self.build_subplots_pie_chart_test_classes_results
            )
            failed_table_future = executor.submit(self.build_subplots_failed_table)
            skipped_table_future = executor.submit(self.build_subplots_skipped_table)
            summary_table_future = executor.submit(
                self.build_subplots_test_suites_summary_table
            )
            if slowest_test_classes and slowest_test_classes is not None:
                slowest_classes_future = executor.submit(
                    self.build_subplots_top_slowest_test_classes, slowest_test_classes
                )
                slowest_classes_base64 = slowest_classes_future.result()

            # Wait for all futures to complete and retrieve results
            pie_chart_base64 = pie_chart_future.result()
            failed_table_base64 = failed_table_future.result()
            skipped_table_base64 = skipped_table_future.result()
            summary_table_base64 = summary_table_future.result()

        # Generate the HTML report with the results
        self.generate_html_report_to_file(
            output,
            pie_chart_base64,
            failed_table_base64,
            skipped_table_base64,
            summary_table_base64,
            slowest_classes_base64,
        )
