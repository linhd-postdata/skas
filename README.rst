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

.. |commits-since| image:: https://img.shields.io/github/commits-since/linhd-postdata/rantanplan/0.4.2.svg
    :alt: Commits since latest release
    :target: https://github.com/linhd-postdata/rantanplan/compare/0.4.2...master

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

Usage
=====

Install required resources
--------------------------

#. Install spaCy model language for Spanish::

        python -m spacy download es_core_news_md

#. Install Freeling rules for affixes::

        python -m spacy_affixes download es


Import rantanplan
-----------------

To use rantanplan in a project::

        import rantanplan

Usage example
-------------
.. code-block:: python

    from rantanplan.core import get_scansion
    
    poem = """Me gustas cuando callas porque estás como ausente,
    y me oyes desde lejos, y mi voz no te toca.
    Parece que los ojos se te hubieran volado
    y parece que un beso te cerrara la boca.

    Como todas las cosas están llenas de mi alma
    emerges de las cosas, llena del alma mía.
    Mariposa de sueño, te pareces a mi alma,
    y te pareces a la palabra melancolía."""
    
    get_scansion(poem)

Output example
--------------

.. code-block:: python

    [{'tokens': [{'word': [{'syllable': 'Me',
      'is_stressed': False,
      'is_word_end': True}],
    'stress_position': 0},
   {'word': [{'syllable': 'gus', 'is_stressed': True},
     {'syllable': 'tas', 'is_stressed': False, 'is_word_end': True}],
    'stress_position': -2},
   {'word': [{'syllable': 'cuan', 'is_stressed': False},
     {'syllable': 'do', 'is_stressed': False, 'is_word_end': True}],
    'stress_position': 0},
   {'word': [{'syllable': 'ca', 'is_stressed': True},
     {'syllable': 'llas', 'is_stressed': False, 'is_word_end': True}],
    'stress_position': -2},
   {'word': [{'syllable': 'por', 'is_stressed': False},
     {'syllable': 'que',
      'is_stressed': False,
      'has_synalepha': True,
      'is_word_end': True}],
    'stress_position': 0},
   {'word': [{'syllable': 'es', 'is_stressed': False},
     {'syllable': 'tás', 'is_stressed': True, 'is_word_end': True}],
    'stress_position': -1},
   {'word': [{'syllable': 'co', 'is_stressed': False},
     {'syllable': 'mo',
      'is_stressed': False,
      'has_synalepha': True,
      'is_word_end': True}],
    'stress_position': 0},
   {'word': [{'syllable': 'au', 'is_stressed': False},
     {'syllable': 'sen', 'is_stressed': True},
     {'syllable': 'te', 'is_stressed': False, 'is_word_end': True}],
    'stress_position': -2},
   {'symbol': ','}],
  'phonological_groups': [{'syllable': 'Me',
    'is_stressed': False,
    'is_word_end': True},
   {'syllable': 'gus', 'is_stressed': True},
   {'syllable': 'tas', 'is_stressed': False, 'is_word_end': True},
   {'syllable': 'cuan', 'is_stressed': False},
   {'syllable': 'do', 'is_stressed': False, 'is_word_end': True},
   {'syllable': 'ca', 'is_stressed': True},
   {'syllable': 'llas', 'is_stressed': False, 'is_word_end': True},
   {'syllable': 'por', 'is_stressed': False},
   {'syllable': 'quees', 'is_stressed': False, 'synalepha_index': [2]},
   {'syllable': 'tás', 'is_stressed': True, 'is_word_end': True},
   {'syllable': 'co', 'is_stressed': False},
   {'syllable': 'moau', 'is_stressed': False, 'synalepha_index': [1]},
   {'syllable': 'sen', 'is_stressed': True},
   {'syllable': 'te', 'is_stressed': False, 'is_word_end': True}],
  'rhythm': {'stress': '-+---+---+--+-', 'type': 'pattern', 'length': 14}},
   ...

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
