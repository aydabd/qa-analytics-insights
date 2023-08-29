QA Analytics Insights
=====================

.. image:: https://img.shields.io/github/downloads/aydabd/qa-analytics-insights/total
   :alt: GitHub all releases
   :target: https://www.github.com/aydabd/qa-analytics-insights/releases

.. image:: https://github.com/aydabd/qa-analytics-insights/actions/workflows/ci.yml/badge.svg
      :alt: GitHub Workflow Status
      :target: https://www.github.com/aydabd/qa-analytics-insights/actions/workflows/ci.yml

========
Overview
========

This repository hosts the source code for the `QA Analytics Insights`_ project,
a robust command-line interface (CLI) tool designed to generate data-driven
insights from QA (Quality Assurance) test results.

========
Features
========
* Analyze test results in XML format.
* Generate visualizations and metrics to better understand test performance.
* Create actionable insights to improve QA processes.

Command line tool
-----------------

The command line tool can be used to generate insights from the tests results
in xml format.

The tool can be used as follows::

    $ qa-analytics-insights --help
    Usage: qa-analytics-insights -f <file> [-o <output_dir>] [-vv] [-h] [-v]

The tool accepts the following arguments:

    * `-f` or `--file`: Path to the file containing the tests results in xml format.
    * `-o` or `--output`: Path to the directory where the insights will be generated.
    * `-vv` or `--verbose`: Enable verbose mode.
    * `-v` or `--version`: Show version and exit.
    * `-h` or `--help`: Show help message and exit.


Library
-------

The library can be used to generate insights from the tests result in xml
format.

The library can be used as follows::

    from qa_analytics_insights.result_analyzer import ResultAnalyzer
    analyzer = ResultAnalyzer(
        test_results_file_path='path/to/test/results/file.xml',
        output_dir='path/to/output/dir',
    )

============
Installation
============

To install the package from `pypi`_, run the following command::

    $ pip install qa-analytics-insights

===========
Development
===========

To install the package in development mode, run the following command::

    # create a virtual environment
    $ virtualenv -p python3 venv

    # activate the virtual environment
    $ source venv/bin/activate

    # Run the package in development mode
    $ hatch run develop:all


For linting, run the following command::

    $ hatch run linter:linter

for building the package, run the following command::

    $ hatch build

for generating the documentation, run the following command::

    $ hatch run docs:all

for running the tests with coverage, run the following command::

    $ hatch run default:all

.. _QA Analytics Insights : https://qa-analytics-insights.readthedocs.io/en/latest/
.. _pypi: https://pypi.org/project/pip/qa-analytics-insights
