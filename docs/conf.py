"""Sphinx configuration."""
import inspect
import os
import sys
import shutil

from docutils import nodes

from qa_analytics_insights._version import __version__


def update_version_badge(app: object, doctree: object, docname: str) -> None:
    """Update the version badge in the documentation to match the package version.

    This function is called by Sphinx when the doctree-read event is emitted.
    This event is emitted when the doctree is read from disk and ready to be
    processed. See: https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx-core-events
    
    Args:
        app: The Sphinx application object.
        doctree: The document tree.
        docname: The document name.
    """
    # Extract the version information from the package
    package_version = __version__
    
    for image_node in doctree.traverse(nodes.image):
        original_url = image_node['uri']

        # Identify the image node to update by matching a unique part of its URL
        if 'img.shields.io/badge/qa_analytics_insights-<version>-blue' in original_url:
            # Create a new URL with the updated version information
            new_url = (
                f"https://img.shields.io/badge/qa_analytics_insights-{package_version}-blue"
            )
            
            # Update the image node URL
            image_node['uri'] = new_url

def setup(app):
    app.connect('doctree-resolved', update_version_badge)

# -- Path setup --------------------------------------------------------------

__location__ = os.path.join(os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe())))

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.join(__location__, "../src"))

# -- Run sphinx-apidoc -------------------------------------------------------
# This hack is necessary since RTD does not issue `sphinx-apidoc` before running
# `sphinx-build -b html . _build/html`. See Issue:
# https://github.com/readthedocs/readthedocs.org/issues/1139
# DON'T FORGET: Check the box "Install your project inside a virtualenv using
# setup.py install" in the RTD Advanced Settings.
# Additionally it helps us to avoid running apidoc manually

try:  # for Sphinx >= 1.7
    from sphinx.ext import apidoc
except ImportError:
    from sphinx import apidoc

output_dir = os.path.join(__location__, "api")
module_dir = os.path.join(__location__, "../src/qa_analytics_insights")
try:
    shutil.rmtree(output_dir)
except FileNotFoundError:
    pass

try:
    import sphinx

    cmd_line = f"sphinx-apidoc --implicit-namespaces -f -o {output_dir} {module_dir}"

    args = cmd_line.split(" ")
    if tuple(sphinx.__version__.split(".")) >= ("3", "5", "2"):
        # This is a rudimentary parse_version to avoid external dependencies
        args = args[1:]

    apidoc.main(args)
except Exception as e:
    print(f"Running `sphinx-apidoc` failed!\n{e}")

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.ifconfig",
    "sphinx.ext.mathjax",
    "sphinx_rtd_theme",
    "sphinx.ext.napoleon",
    "sphinx_tabs.tabs",
    "sphinx-prompt",
    "sphinx_toolbox",
]

github_username = "aydabd"
github_repository = "qa-analytics-insights"
autodoc_mock_imports = ["loguru"]
# autodoc_typehints = "none"
always_document_param_types = True
typehints_defaults = "braces-after"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "qa-analytics-insights"
copyright = "2023, Aydin Abdi"
author = "Aydin Abdi"

# The full version, including alpha/beta/rc tags.
version = __version__
if not version or version.lower() == "unknown":
    version = os.getenv("READTHEDOCS_VERSION", "unknown")  # automatically set by RTD

release = version


# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".venv"]

# If this is True, todo emits a warning for each TODO entries. The default is False.
todo_emit_warnings = True

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "canonical_url": "",
    "analytics_id": "UA-XXXXXXX-1",  #  Provided by Google in your dashboard
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "style_nav_header_background": "#2980B9",
    # Toc options
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 2,
    "includehidden": True,
    "titles_only": False,
}

# Output file base name for HTML help builder.
htmlhelp_basename = "qa-analytics-insights-doc"

print(f"loading configurations for {project} {version} ...", file=sys.stderr)

