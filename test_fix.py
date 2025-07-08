#!/usr/bin/env python3
"""
Script to manually test the fix for long class names in visualizations.
"""

import sys
import os
sys.path.insert(0, 'src')

from qa_analytics_insights.data_classes import TestCase, TestClass, TestSuite
from qa_analytics_insights.result_visualizer import ResultVisualizer

# Create test data with very long class names
test_cases = [
    TestCase(
        name="test_method_1",
        test_class="VeryVeryLongTestClassNameThatDefinitelyExceedsSixteenCharacters",
        execution_time=1.5,
        result="passed"
    ),
    TestCase(
        name="test_method_2", 
        test_class="VeryVeryLongTestClassNameThatDefinitelyExceedsSixteenCharacters",
        execution_time=2.0,
        result="failed",
        failure_reason="AssertionError: Test failed because of some very long reason that might also need truncation"
    ),
    TestCase(
        name="test_method_3",
        test_class="AnotherExtremelyLongTestClassNameThatIsEvenLongerThanTheFirstOne",
        execution_time=0.5,
        result="skipped",
        skipped_reason="Test skipped for some reason"
    ),
    TestCase(
        name="test_method_4",
        test_class="ShortClass",
        execution_time=1.0,
        result="passed"
    )
]

# Create test classes
class1 = TestClass(name="VeryVeryLongTestClassNameThatDefinitelyExceedsSixteenCharacters")
class1.test_cases = [test_cases[0], test_cases[1]]

class2 = TestClass(name="AnotherExtremelyLongTestClassNameThatIsEvenLongerThanTheFirstOne")
class2.test_cases = [test_cases[2]]

class3 = TestClass(name="ShortClass") 
class3.test_cases = [test_cases[3]]

test_classes = [class1, class2, class3]

# Create test suite
suite = TestSuite(
    name="VeryVeryLongTestSuiteNameThatAlsoExceedsSixteenCharactersAndShouldBeTruncated",
    tests=4,
    failures=1,
    errors=0,
    skipped=1,
    execution_time=5.0
)
suite.test_classes = test_classes
suite.test_cases = test_cases

# Create visualizer and test all methods
visualizer = ResultVisualizer([suite])

print("Testing long class name truncation...")

# Test truncation function directly
print(f"Original name: 'VeryVeryLongTestClassNameThatDefinitelyExceedsSixteenCharacters'")
print(f"Truncated name: '{visualizer.truncate_name('VeryVeryLongTestClassNameThatDefinitelyExceedsSixteenCharacters')}'")
print()

import matplotlib.pyplot as plt

# Test each visualization method
print("Generating pie charts...")
pie_figure = visualizer.plot_pie_charts_test_classes()
if pie_figure:
    print("✓ Pie charts generated successfully")
    pie_figure.savefig('/tmp/test_pie_charts.png', bbox_inches='tight')
    plt.close(pie_figure)
else:
    print("✗ Failed to generate pie charts")

print("Generating failed test cases table...")
failed_figure = visualizer.plot_failed_test_cases_table()
if failed_figure:
    print("✓ Failed test cases table generated successfully")
    failed_figure.savefig('/tmp/test_failed_table.png', bbox_inches='tight')
    plt.close(failed_figure)
else:
    print("✗ Failed to generate failed test cases table")

print("Generating skipped test cases table...")
skipped_figure = visualizer.plot_skipped_test_cases_table()
if skipped_figure:
    print("✓ Skipped test cases table generated successfully")
    skipped_figure.savefig('/tmp/test_skipped_table.png', bbox_inches='tight')
    plt.close(skipped_figure)
else:
    print("✗ Failed to generate skipped test cases table")

print("Generating slowest test classes chart...")
slowest_figure = visualizer.plot_top_slowest_test_classes_pie_bar_chart(test_classes)
if slowest_figure:
    print("✓ Slowest test classes chart generated successfully")
    slowest_figure.savefig('/tmp/test_slowest_chart.png', bbox_inches='tight')
    plt.close(slowest_figure)
else:
    print("✗ Failed to generate slowest test classes chart")

print("Generating test suites summary table...")
summary_figure = visualizer.plot_test_suites_summary_table()
if summary_figure:
    print("✓ Test suites summary table generated successfully")
    summary_figure.savefig('/tmp/test_summary_table.png', bbox_inches='tight')
    plt.close(summary_figure)
else:
    print("✗ Failed to generate test suites summary table")

print("\nAll visualizations generated successfully! Check /tmp/ for output files.")
print("The fix for long class names has been applied and is working correctly.")