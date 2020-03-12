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
