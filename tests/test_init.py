"""Tests for __init__ module."""

import qa_analytics_insights


def test_module_imports():
    """Test that the module can be imported and has required attributes."""
    assert hasattr(qa_analytics_insights, '__author__')
    assert hasattr(qa_analytics_insights, '__license__')
    assert hasattr(qa_analytics_insights, '__version__')


def test_author():
    """Test author attribute."""
    assert qa_analytics_insights.__author__ == "Aydin Abdi"


def test_license():
    """Test license attribute."""
    assert qa_analytics_insights.__license__ == "MIT"


def test_version():
    """Test version attribute exists."""
    assert qa_analytics_insights.__version__ is not None
    assert isinstance(qa_analytics_insights.__version__, str)