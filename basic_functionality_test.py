#!/usr/bin/env python3
"""Basic functionality test script for qa-analytics-insights.

This script tests core functionality without requiring pytest or other testing frameworks.
It can be used for quick validation in environments where the full test suite cannot run.
"""

import sys
import tempfile
import os
from pathlib import Path
from xml.etree import ElementTree as ET


def test_imports():
    """Test that all modules can be imported successfully."""
    print("=== Testing Module Imports ===")
    
    try:
        import qa_analytics_insights
        from qa_analytics_insights.data_classes import TestCase, TestClass, TestSuite
        from qa_analytics_insights.parser import ParserTestCase, ParserTestSuite
        from qa_analytics_insights.result_visualizer import ResultVisualizer
        from qa_analytics_insights.xml_loader import XMLLoader
        from qa_analytics_insights.xml_parser import XMLParser
        from qa_analytics_insights.result_analyzer import ResultAnalyzer
        from qa_analytics_insights.cli import main, ArgsParser, Cli
        
        print("✓ All core module imports successful")
        
        # Test module attributes
        assert hasattr(qa_analytics_insights, '__author__')
        assert hasattr(qa_analytics_insights, '__license__')
        assert hasattr(qa_analytics_insights, '__version__')
        assert qa_analytics_insights.__author__ == "Aydin Abdi"
        assert qa_analytics_insights.__license__ == "MIT"
        print("✓ Module attributes correct")
        
        return True
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False


def test_data_classes():
    """Test data classes functionality."""
    print("\n=== Testing Data Classes ===")
    
    try:
        from qa_analytics_insights.data_classes import TestCase, TestClass, TestSuite
        
        # Test TestCase
        test_case = TestCase(name="test_example")
        assert test_case.name == "test_example"
        assert test_case.test_module is None
        assert test_case.test_class is None
        assert test_case.execution_time == 0.0
        assert test_case.result == "passed"
        print("✓ TestCase basic functionality")
        
        # Test TestCase with custom values
        test_case = TestCase(
            name="test_custom",
            test_module="test_module",
            test_class="TestClass",
            execution_time=1.5,
            result="failed",
            timestamp="2023-01-01T00:00:00",
            failure_reason="assertion error"
        )
        assert test_case.name == "test_custom"
        assert test_case.test_module == "test_module"
        assert test_case.test_class == "TestClass"
        assert test_case.execution_time == 1.5
        assert test_case.result == "failed"
        print("✓ TestCase with custom values")
        
        # Test TestClass
        test_class = TestClass(name="TestExample")
        assert test_class.name == "TestExample"
        assert test_class.test_cases == []
        assert test_class.passed == 0
        assert test_class.failed == 0
        assert test_class.skipped == 0
        assert test_class.errors == 0
        print("✓ TestClass basic functionality")
        
        # Test TestClass with test cases
        test_case1 = TestCase(name="test1", execution_time=1.0, result="passed")
        test_case2 = TestCase(name="test2", execution_time=2.0, result="failed")
        test_case3 = TestCase(name="test3", execution_time=0.5, result="skipped")
        test_case4 = TestCase(name="test4", execution_time=1.5, result="error")
        
        test_class = TestClass(name="TestWithCases", test_cases=[test_case1, test_case2, test_case3, test_case4])
        assert test_class.passed == 1
        assert test_class.failed == 1
        assert test_class.skipped == 1
        assert test_class.errors == 1
        assert test_class.execution_time == 5.0
        assert len(test_class.failed_test_cases) == 1
        assert len(test_class.skipped_test_cases) == 1
        assert len(test_class.error_test_cases) == 1
        print("✓ TestClass with test cases")
        
        # Test TestSuite
        test_suite = TestSuite()
        assert test_suite.name is None
        assert test_suite.tests == 0
        assert test_suite.passed == 0
        print("✓ TestSuite basic functionality")
        
        test_suite = TestSuite(
            name="test_suite",
            tests=10,
            errors=1,
            failures=2,
            skipped=1,
            execution_time=15.5,
            timestamp="2023-01-01T00:00:00"
        )
        assert test_suite.name == "test_suite"
        assert test_suite.tests == 10
        assert test_suite.passed == 6  # 10 - 1 - 2 - 1 = 6
        print("✓ TestSuite with custom values")
        
        return True
    except Exception as e:
        print(f"✗ Data classes test failed: {e}")
        return False


def test_type_fixes():
    """Test that type annotation fixes are working."""
    print("\n=== Testing Type Annotation Fixes ===")
    
    try:
        from qa_analytics_insights.xml_loader import XMLLoader
        from qa_analytics_insights.result_visualizer import ResultVisualizer
        from qa_analytics_insights.data_classes import TestSuite
        
        # Test XMLLoader type fix with actual file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write('<?xml version="1.0"?><root><test>content</test></root>')
            temp_path = f.name
        
        try:
            loader = XMLLoader(temp_path)
            tree = loader.tree
            root = loader.root
            assert root.tag == "root"
            print("✓ XMLLoader type annotations working")
        finally:
            os.unlink(temp_path)
        
        # Test ResultVisualizer truncate_name with None
        result = ResultVisualizer.truncate_name(None)
        assert result == "N/A"
        print("✓ ResultVisualizer.truncate_name handles None")
        
        result = ResultVisualizer.truncate_name("test_name_that_is_very_long_and_should_be_truncated")
        assert len(result) <= 16
        assert result.endswith("...")
        print("✓ ResultVisualizer.truncate_name truncates long names")
        
        # Test with TestSuite name
        test_suite = TestSuite(name=None)
        result = ResultVisualizer.truncate_name(test_suite.name)
        assert result == "N/A"
        print("✓ ResultVisualizer.truncate_name works with TestSuite.name")
        
        return True
    except Exception as e:
        print(f"✗ Type fixes test failed: {e}")
        return False


def test_parser_functionality():
    """Test parser functionality with various XML formats."""
    print("\n=== Testing Parser Functionality ===")
    
    try:
        from qa_analytics_insights.parser import ParserTestCase, ParserTestSuite
        
        # Test ParserTestSuite
        xml_content = '''
        <testsuite name="TestSuite" tests="5" errors="1" failures="2" 
                   skipped="1" time="10.5" timestamp="2023-01-01T00:00:00">
        </testsuite>
        '''
        root = ET.fromstring(xml_content)
        parser = ParserTestSuite(root)
        test_suite = parser.parse()
        
        assert test_suite.name == "TestSuite"
        assert test_suite.tests == 5
        assert test_suite.errors == 1
        assert test_suite.failures == 2
        assert test_suite.skipped == 1
        assert test_suite.execution_time == 10.5
        assert test_suite.timestamp == "2023-01-01T00:00:00"
        print("✓ ParserTestSuite basic parsing")
        
        # Test ParserTestCase with single class name (bug fix test)
        xml_content = '''
        <testcase name="test_example" classname="TestClass" 
                  time="1.5" timestamp="2023-01-01T00:00:00">
        </testcase>
        '''
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)
        test_case = parser.parse()
        
        assert test_case.name == "test_example"
        assert test_case.test_class == "TestClass"
        assert test_case.test_module == ""  # Should be empty for single part classname
        assert test_case.execution_time == 1.5
        assert test_case.result == "passed"
        print("✓ ParserTestCase single classname (bug fix)")
        
        # Test ParserTestCase with module.class format
        xml_content = '''
        <testcase name="test_example" classname="test_module.TestClass" 
                  time="1.5">
        </testcase>
        '''
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)
        test_case = parser.parse()
        
        assert test_case.name == "test_example"
        assert test_case.test_class == "TestClass"
        assert test_case.test_module == "test_module"
        print("✓ ParserTestCase module.class format")
        
        # Test ParserTestCase with failure
        xml_content = '''
        <testcase name="test_failed" classname="TestClass" time="1.5">
            <failure message="assertion failed">
                Detailed failure message here
            </failure>
        </testcase>
        '''
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)
        test_case = parser.parse()
        
        assert test_case.result == "failed"
        assert test_case.failure_reason is not None
        print("✓ ParserTestCase with failure")
        
        # Test ParserTestCase with error
        xml_content = '''
        <testcase name="test_error" classname="TestClass" time="1.5">
            <error message="runtime error">
                Detailed error message here
            </error>
        </testcase>
        '''
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)
        test_case = parser.parse()
        
        assert test_case.result == "error"
        assert test_case.error_reason is not None
        print("✓ ParserTestCase with error")
        
        # Test ParserTestCase with skipped
        xml_content = '''
        <testcase name="test_skipped" classname="TestClass" time="0.0">
            <skipped message="not applicable">
                Skipped reason here
            </skipped>
        </testcase>
        '''
        root = ET.fromstring(xml_content)
        parser = ParserTestCase(root)
        test_case = parser.parse()
        
        assert test_case.result == "skipped"
        assert test_case.skipped_reason is not None
        print("✓ ParserTestCase with skipped")
        
        return True
    except Exception as e:
        print(f"✗ Parser functionality test failed: {e}")
        return False


def main():
    """Run all basic functionality tests."""
    print("QA Analytics Insights - Basic Functionality Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_data_classes,
        test_type_fixes,
        test_parser_functionality,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} crashed: {e}")
            failed += 1
    
    print(f"\n{'=' * 50}")
    print(f"Test Results:")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Total:  {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All basic functionality tests passed!")
        return True
    else:
        print(f"\n❌ {failed} test(s) failed!")
        return False


if __name__ == "__main__":
    # Add src to path for imports
    current_dir = Path(__file__).parent
    src_dir = current_dir / "src"
    sys.path.insert(0, str(src_dir))
    
    success = main()
    sys.exit(0 if success else 1)