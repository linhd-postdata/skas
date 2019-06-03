========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |requires|
        | |coveralls| |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/rantanplan/badge/?style=flat
    :target: https://readthedocs.org/projects/rantanplan
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/linhd-postdata/rantanplan.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/linhd-postdata/rantanplan

.. |requires| image:: https://requires.io/github/linhd-postdata/rantanplan/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/linhd-postdata/rantanplan/requirements/?branch=master

.. |coveralls| image:: https://coveralls.io/repos/linhd-postdata/rantanplan/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/linhd-postdata/rantanplan

.. |codecov| image:: https://codecov.io/github/linhd-postdata/rantanplan/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/linhd-postdata/rantanplan

.. |version| image:: https://img.shields.io/pypi/v/rantanplan.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/rantanplan

.. |commits-since| image:: https://img.shields.io/github/commits-since/linhd-postdata/rantanplan/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/linhd-postdata/rantanplan/compare/v0.1.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/rantanplan.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/rantanplan

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/rantanplan.svg
    :alt: Supported versions
    :target: https://pypi.org/project/rantanplan

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/rantanplan.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/rantanplan


.. end-badges

Scansion tool for Spanish texts

* Free software: Apache Software License 2.0

Installation
============

::

    pip install rantanplan

Documentation
=============


https://rantanplan.readthedocs.io/


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
