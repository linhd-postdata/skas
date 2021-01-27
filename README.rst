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

Rantanplan is a Python library for the automated scansion of Spanish poetry. Scansion is the measurement of the rhythm of verses of a poem and our tool achieves state-of-the-art results for mixed metre poems. It is also able to identify up to 45 different types of the most significant Spanish stanzas. Rantanplan is fast and accurate as it is built using SpaCy and SpaCy-affixes.

* Free software: Apache Software License 2.0

Installation
============

::

    pip install rantanplan


Install required resources
--------------------------

#. Install spaCy model language for Spanish::

        python -m spacy download es_core_news_md

#. Install Freeling rules for affixes::

        python -m spacy_affixes download es


Usage
=====


Import Rantanplan
-----------------

To use Rantanplan in a project::

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


The output of Rantanplan is a complex structure that will be broken down for clarity.

First, Rantanplan will show a list of stanzas. Each stanza is then shown as two separate lists. A list of tokens, and a list of "phonological groups" i.e., the phonological units that form a verse after synalephas and sinaereris are taken into account.


Tokens
######


If the token is a word, it shows a list of the syllables it is made of, with the following information:

* *syllable*: The text of the syllable.

* *is_stressed*: Whether the syllable is stressed or not.

* *is_word_end*: Whether the syllable is the end of a word or not.

* *has_synalepha* or *has_sinaeresis*: Whether or not the syllable can be conjoined with the next one.

* *stress_position*: Index, starting from 0, for the stressed syllable of the word. If the index is negative, the syllable position is counted from the end of the word:

  * 0: First syllable

  * -1: Last syllable

  * -2: Penultimate syllable

  * *etc*

If the token is a not a word, it is shown as `symbol`.

List of tokens example
######################

.. code-block:: python

    {'tokens': [{'word': [{'syllable': 'co', 'is_stressed': False},
       {'syllable': 'mo',
        'is_stressed': False,
        'has_synalepha': True,
        'is_word_end': True}],
      'stress_position': 0},
     {'word': [{'syllable': 'au', 'is_stressed': False}
   ...
     {'symbol': ','}],
   ...


Phonological groups
###################
The next element of the output is a list of `phonological groups`. We use this term to refer to the phonological unit that makes up a poem when it is read, after synalephas and sinaereris are taken into account.

Phonological groups are quite similar to the token list but have no word boundaries because this is lost when applying synalephas. Each syllable within `phonological_groups` can carry the following information:

* *syllable*: The text of the syllable.

* *is_stressed*: Whether the syllable is stressed or not.

* *is_word_end*: Whether the syllable is the end of a word or not.

* *synalepha_index* or *sinaeresis_index*: The index of the character where the syllable is conjoined with the next one:

  * 0: No synalepha or sinaeresis has been realised.

  * Any other number: List of indexes on the syllable, starting from 0, where the original syllable or syllables have been conjoined with the next one:

    * Example: The syllable `moau` was originally split at position `1`:

      .. code-block:: python

        {'syllable': 'moau', 'is_stressed': False, 'synalepha_index': [1]}


    * Indexes of the syllable:

      ``m o a u``

      ``0 1 2 3``

      We split at position `1`: `o`, so then, we know that the original syllables are `mo` and `au`

Phonological groups example
###########################


.. code-block:: python

  {'phonological_groups': [{'syllable': 'Me',
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



Metrical information
####################


Finally, at the verse level we find information about the verse itself on the `rhythm` key:

* *rhythm*: Pattern of the unstressed (`-`) and stressed (`+`) syllable. This output can be changed with the parameter `rhythm_format`. You can find more information about how this parameter works on the documentation.

* *length*: Proposed length for the verse.

* *length_range*: Minimum and maximum verse length possible. This is calculated taking into account all possible sinaeresis and synalephas.


Metrical information example
############################


.. code-block:: python

  'rhythm': {'stress': '---+----+----+-',
   'length': 14,
   'length_range': {'min_length': 15, 'max_length': 17}},
   ...



Stanza detection
################

Rantanplan is also able to detect the stanza type from a list of popular Spanish stanzas and . The complete

When this option is enabled with the `rhyme_analysis`, additional information about the stanza is shown on the output.

If we take this "cuarteto" for example:

::

  Yo persigo una forma que no encuentra mi estilo,
  botón de pensamiento que busca ser la rosa;
  se anuncia con un beso que en mis labios se posa
  al abrazo imposible de la Venus de Milo

If we call `get_scansion` with the `rhyme_analysis` parameter set to `True`, the following information is added to the analysis of each line:

* *structure*: The name of the stanza that has been detected

* *rhyme*: A letter code to match rhyming verses. In this example, verse 1 rhymes with verse 4, and verse 2 rhymes with verse 3, and a letter is assigned to verses that rhyme together as shown below:

  ::

    Yo persigo una forma que no encuentra mi estilo,  a
    botón de pensamiento que busca ser la rosa;       b
    se anuncia con un beso que en mis labios se posa  b
    al abrazo imposible de la Venus de Milo           a


* *ending*: What part of the last word is rhyming.

* *ending_stress*: Negative index (-1 for last, -2 for penultimate, etc.) for the vowel that carries the stress of the rhyming part.

* *rhyme_type*: Whether the rhyme is consonant or assonant:
    * Consonant: All characters from the last stressed vowel to the end the the word coincide on verses that rhyme. For example:
      ::

        estILO
        mILO

    * Assonant: Same as consonant rhyme but only if all vowels match:
      ::

        amAdO
        cachArrO


* *rhyme_relaxation*: Whether ot not rules for rhyme relaxation are applied. For example, removing weak vowels on diphthongs or making letters match when they are pronounced the same, for example `c` and `z`.


Stanza detection example
########################

.. code-block:: python

  'structure': 'cuarteto',
  'rhyme': 'a',
  'ending': 'ilo',
  'ending_stress': -3,
  'rhyme_type': 'consonant',
  'rhyme_relaxation': True},
   ...


Full output example
###################


A complete example of Rantanplan output is shown here:

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

