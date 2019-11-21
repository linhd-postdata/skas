# -*- coding: utf-8 -*-
import json
from pathlib import Path

import pytest

from rantanplan.rhymes import STRUCTURES
from rantanplan.rhymes import analyze_rhyme
from rantanplan.rhymes import assign_letter_codes
from rantanplan.rhymes import get_clean_codes
from rantanplan.rhymes import get_rhymes
from rantanplan.rhymes import get_stressed_endings
from rantanplan.rhymes import rhyme_codes_to_letters
from rantanplan.rhymes import search_structure
from rantanplan.rhymes import split_stress


@pytest.fixture
def stressed_endings():
    return [
        (['ma', 'yo'], 9, -2),
        (['lor'], 7, -1),
        (['ca', 'ñan'], 8, -2),
        (['flor'], 8, -1),
        (['lan', 'dria'], 8, -2),
        (['ñor'], 8, -1),
        (['ra', 'dos'], 8, -2),
        (['mor'], 7, -1),
        (['ta', 'do'], 8, -2),
        (['sión'], 8, -1),
        (['dí', 'a'], 9, -2),
        (['son'], 7, -1),
        (['ci', 'lla'], 9, -2),
        (['bor'], 8, -1),
        (['te', 'ro'], 9, -2),
        (['dón'], 7, -1),
    ]


@pytest.fixture
def haiku():
    return json.loads(Path("tests/fixtures/haiku.json").read_text())


@pytest.fixture
def sonnet():
    return json.loads(Path("tests/fixtures/sonnet.json").read_text())


@pytest.fixture
def couplet():
    return json.loads(Path("tests/fixtures/couplet.json").read_text())


@pytest.fixture
def romance():
    return json.loads(Path("tests/fixtures/romance.json").read_text())


def test_get_stressed_endings():
    # plátano
    # mano
    # prisión
    lines = [
        {'tokens': [{'word': [{'syllable': 'plá', 'is_stressed': True},
                              {'syllable': 'ta', 'is_stressed': False},
                              {'syllable': 'no', 'is_stressed': False}],
                     'stress_position': -3}],
         'phonological_groups': [{'syllable': 'plá', 'is_stressed': True},
                                 {'syllable': 'ta', 'is_stressed': False},
                                 {'syllable': 'no', 'is_stressed': False}],
         'rhythm': {'rhythmical_stress': '+-', 'type': 'pattern'},
         'rhythmical_length': 2},
        {'tokens': [{'word': [{'syllable': 'ma', 'is_stressed': True},
                              {'syllable': 'no', 'is_stressed': False}],
                     'stress_position': -2}],
         'phonological_groups': [{'syllable': 'ma', 'is_stressed': True},
                                 {'syllable': 'no', 'is_stressed': False}],
         'rhythm': {'rhythmical_stress': '+-', 'type': 'pattern'},
         'rhythmical_length': 2},
        {'tokens': [{'word': [{'syllable': 'pri', 'is_stressed': False},
                              {'syllable': 'sión', 'is_stressed': True}],
                     'stress_position': -1}],
         'phonological_groups': [{'syllable': 'pri', 'is_stressed': False},
                                 {'syllable': 'sión',
                                  'is_stressed': True}],
         'rhythm': {'rhythmical_stress': '-+-', 'type': 'pattern'},
         'rhythmical_length': 3}
    ]
    output = [
        (['plá', 'ta', 'no'], 3, -3),
        (['ma', 'no'], 2, -2),
        (['sión'], 2, -1)
    ]
    assert get_stressed_endings(lines) == output


def test_get_clean_codes(stressed_endings):
    # Consonant rhyme by default
    output = (
        {0: 'Ayo', 1: 'OR', 2: 'Añan', 3: 'ANdria', 4: 'Ados', 5: 'Ado',
         6: 'ION', 7: 'Ia', 8: 'ON', 9: 'Illa', 10: 'Ero'},
        [0, 1, 2, 1, 3, 1, 4, 1, 5, 6, 7, 8, 9, 1, 10, 8],
        {0, 2, 3, 4, 5, 6, 7, 9, 10},
    )
    assert get_clean_codes(stressed_endings) == output
    assert get_clean_codes(stressed_endings, False, False) == output


def test_get_clean_codes_assonance(stressed_endings):
    output = (
        {0: 'Ao', 1: 'O', 2: 'Aa', 3: 'Aia', 4: 'IO', 5: 'Ia', 6: 'Eo'},
        [0, 1, 2, 1, 3, 1, 0, 1, 0, 4, 5, 1, 5, 1, 6, 1],
        {2, 3, 4, 6},
    )
    assert get_clean_codes(stressed_endings, assonance=True) == output
    assert get_clean_codes(stressed_endings, True, False) == output


def test_get_clean_codes_relaxation(stressed_endings):
    output = (
        {0: 'Ayo', 1: 'OR', 2: 'Añan', 3: 'ANdra', 4: 'Ados', 5: 'Ado',
         6: 'ON', 7: 'Ia', 8: 'Illa', 9: 'Ero'},
        [0, 1, 2, 1, 3, 1, 4, 1, 5, 6, 7, 6, 8, 1, 9, 6],
        {0, 2, 3, 4, 5, 7, 8, 9},
    )
    assert get_clean_codes(stressed_endings, relaxation=True) == output
    assert get_clean_codes(stressed_endings, False, True) == output


def test_get_clean_codes_assonance_relaxation(stressed_endings):
    output = (
        {0: 'Ao', 1: 'O', 2: 'Aa', 3: 'Ia', 4: 'Eo'},
        [0, 1, 2, 1, 2, 1, 0, 1, 0, 1, 3, 1, 3, 1, 4, 1],
        {4},
    )
    assert get_clean_codes(
        stressed_endings, assonance=True, relaxation=True) == output
    assert get_clean_codes(stressed_endings, True, True) == output


def get_assign_letter_codes():
    clean_codes = (
        {0: 'Ao', 1: 'O', 2: 'Aa', 3: 'Ia', 4: 'Eo'},
        [0, 1, 2, 1, 2, 1, 0, 1, 0, 1, 3, 1, 3, 1, 4, 1],
        {4},
    )
    output = (
        [0, 1, 2, 1, 2, 1, 0, 1, 0, 1, 3, 1, 3, 1, -1, 1],
        ['Ao', 'O', 'Aa', 'O', 'Aa', 'O', 'Ao', 'O',
         'Ao', 'O', 'Ia', 'O', 'Ia', 'O', '', 'O']
    )
    assert assign_letter_codes(*clean_codes) == output
    assert assign_letter_codes(*clean_codes, offset=None) == output


def get_assign_letter_codes_offset():
    clean_codes = (
        {0: 'Ao', 1: 'O', 2: 'Aa', 3: 'Ia', 4: 'Eo'},
        [0, 1, 2, 1, 2, 1, 0, 1, 0, 1, 3, 1, 3, 1, 4, 1],
        {4},
    )
    output = (
        [-1, 1, 2, 1, 2, 1, 0, 1, 0, 1, 3, 1, 3, 1, -1, 1],
        ['', 'O', 'Aa', 'O', 'Aa', 'O', 'Ao', 'O',
         'Ao', 'O', 'Ia', 'O', 'Ia', 'O', '', 'O']
    )
    assert assign_letter_codes(*clean_codes) == output
    assert assign_letter_codes(*clean_codes, offset=4) == output


def test_sort_rhyme_letters():
    rhymes_codes = [-1, 1, 2, 1, 2, 1, 0, 1, 0, 1, 3, 1, 3, 1, -1, 1]
    output = ['-', 'a', 'b', 'a', 'b', 'a', 'c', 'a',
              'c', 'a', 'd', 'a', 'd', 'a', '-', 'a']
    assert rhyme_codes_to_letters(rhymes_codes) == output


def test_sort_rhyme_letters_unrhymed():
    rhymes_codes = [-1, 1, 2, 1, 2, 1, 0, 1, 0, 1, 3, 1, 3, 1, -1, 1]
    output = ['$', 'a', 'b', 'a', 'b', 'a', 'c', 'a',
              'c', 'a', 'd', 'a', 'd', 'a', '$', 'a']
    assert rhyme_codes_to_letters(rhymes_codes, "$") == output


def test_split_stress():
    endings = ['', 'O', 'Aa', 'O', 'Aa', 'O', 'Ao', 'O',
               'Ao', 'O', 'Ia', 'O', 'Ia', 'O', '', 'O']
    output = (
        [0, -1, -2, -1, -2, -1, -2, -1, -2, -1, -2, -1, -2, -1, 0, -1],
        ['', 'o', 'aa', 'o', 'aa', 'o', 'ao', 'o',
         'ao', 'o', 'ia', 'o', 'ia', 'o', '', 'o']
    )
    assert split_stress(endings) == output


def test_get_rhymes(stressed_endings):
    output = (
        ['-', 'a', '-', 'a', '-', 'a', '-', 'a',
         '-', '-', '-', 'b', '-', 'a', '-', 'b'],
        ['', 'or', '', 'or', '', 'or', '', 'or',
         '', '', '', 'on', '', 'or', '', 'on'],
        [0, -2, 0, -2, 0, -2, 0, -2, 0, 0, 0, -2, 0, -2, 0, -2],
    )
    assert get_rhymes(
        stressed_endings
    ) == output


def test_get_rhymes_assonance(stressed_endings):
    output = (
        ['a', 'b', '-', 'b', '-', 'b', 'a', 'b',
         'a', '-', 'c', 'b', 'c', 'b', '-', 'b'],
        ['ao', 'o', '', 'o', '', 'o', 'ao', 'o',
         'ao', '', 'ia', 'o', 'ia', 'o', '', 'o'],
        [-2, -1, 0, -1, 0, -1, -2, -1, -2, 0, -2, -1, -2, -1, 0, -1],
    )
    assert get_rhymes(
        stressed_endings, assonance=True
    ) == output


def test_get_rhymes_relaxation(stressed_endings):
    output = (
        ['-', 'a', '-', 'a', '-', 'a', '-', 'a',
         '-', 'b', '-', 'b', '-', 'a', '-', 'b'],
        ['', 'or', '', 'or', '', 'or', '', 'or',
         '', 'on', '', 'on', '', 'or', '', 'on'],
        [0, -2, 0, -2, 0, -2, 0, -2, 0, -2, 0, -2, 0, -2, 0, -2],
    )
    assert get_rhymes(
        stressed_endings, relaxation=True
    ) == output


def test_get_rhymes_assonance_relaxation(stressed_endings):
    output = (
        ['a', 'b', 'c', 'b', 'c', 'b', 'a', 'b',
         'a', 'b', 'd', 'b', 'd', 'b', '-', 'b'],
        ['ao', 'o', 'aa', 'o', 'aa', 'o', 'ao',
         'o', 'ao', 'o', 'ia', 'o', 'ia', 'o', '', 'o'],
        [-2, -1, -2, -1, -2, -1, -2, -1, -2, -1, -2, -1, -2, -1, 0, -1],
    )
    assert get_rhymes(
        stressed_endings, assonance=True, relaxation=True
    ) == output


def test_get_rhymes_offset(stressed_endings):
    output = (
        ['-', 'a', '-', 'a', '-', 'a', '-', '-',
         '-', '-', '-', 'b', '-', 'a', '-', 'b'],
        ['', 'or', '', 'or', '', 'or', '', '',
         '', '', '', 'on', '', 'or', '', 'on'],
        [0, -2, 0, -2, 0, -2, 0, 0, 0, 0, 0, -2, 0, -2, 0, -2],
    )
    assert get_rhymes(
        stressed_endings, offset=4
    ) == output


def test_get_rhymes_assonance_offset(stressed_endings):
    output = (
        ['-', 'a', '-', 'a', '-', 'a', 'b', 'a',
         'b', '-', 'c', 'a', 'c', 'a', '-', 'a'],
        ['', 'o', '', 'o', '', 'o', 'ao', 'o',
         'ao', '', 'ia', 'o', 'ia', 'o', '', 'o'],
        [0, -1, 0, -1, 0, -1, -2, -1, -2, 0, -2, -1, -2, -1, 0, -1],
    )
    assert get_rhymes(
        stressed_endings, assonance=True, offset=4
    ) == output


def test_get_rhymes_relaxation_offset(stressed_endings):
    output = (
        ['-', 'a', '-', 'a', '-', 'a', '-', '-',
         '-', 'b', '-', 'b', '-', 'a', '-', 'b'],
        ['', 'or', '', 'or', '', 'or', '', '',
         '', 'on', '', 'on', '', 'or', '', 'on'],
        [0, -2, 0, -2, 0, -2, 0, 0, 0, -2, 0, -2, 0, -2, 0, -2],
    )
    assert get_rhymes(
        stressed_endings, relaxation=True, offset=4
    ) == output


def test_get_rhymes_assonance_relaxation_offset(stressed_endings):
    output = (
        ['-', 'a', 'b', 'a', 'b', 'a', 'c', 'a',
         'c', 'a', 'd', 'a', 'd', 'a', '-', 'a'],
        ['', 'o', 'aa', 'o', 'aa', 'o', 'ao', 'o',
         'ao', 'o', 'ia', 'o', 'ia', 'o', '', 'o'],
        [0, -1, -2, -1, -2, -1, -2, -1, -2, -1, -2, -1, -2, -1, 0, -1],
    )
    assert get_rhymes(
        stressed_endings, assonance=True, relaxation=True, offset=4
    ) == output


def test_get_rhymes_unrhymed(stressed_endings):
    output = (
        ['$', 'a', '$', 'a', '$', 'a', '$', 'a',
         '$', '$', '$', 'b', '$', 'a', '$', 'b'],
        ['', 'or', '', 'or', '', 'or', '', 'or',
         '', '', '', 'on', '', 'or', '', 'on'],
        [0, -2, 0, -2, 0, -2, 0, -2, 0, 0, 0, -2, 0, -2, 0, -2],
    )
    assert get_rhymes(
        stressed_endings, unrhymed_verse_symbol="$"
    ) == output


def test_get_rhymes_assonance_unrhymed(stressed_endings):
    output = (
        ['a', 'b', '$', 'b', '$', 'b', 'a', 'b',
         'a', '$', 'c', 'b', 'c', 'b', '$', 'b'],
        ['ao', 'o', '', 'o', '', 'o', 'ao', 'o',
         'ao', '', 'ia', 'o', 'ia', 'o', '', 'o'],
        [-2, -1, 0, -1, 0, -1, -2, -1, -2, 0, -2, -1, -2, -1, 0, -1],
    )
    assert get_rhymes(
        stressed_endings, assonance=True, unrhymed_verse_symbol="$"
    ) == output


def test_get_rhymes_relaxation_unrhymed(stressed_endings):
    output = (
        ['$', 'a', '$', 'a', '$', 'a', '$', 'a',
         '$', 'b', '$', 'b', '$', 'a', '$', 'b'],
        ['', 'or', '', 'or', '', 'or', '', 'or',
         '', 'on', '', 'on', '', 'or', '', 'on'],
        [0, -2, 0, -2, 0, -2, 0, -2, 0, -2, 0, -2, 0, -2, 0, -2],
    )
    assert get_rhymes(
        stressed_endings, relaxation=True, unrhymed_verse_symbol="$"
    ) == output


def test_get_rhymes_assonance_relaxation_unrhymed(stressed_endings):
    output = (
        ['a', 'b', 'c', 'b', 'c', 'b', 'a', 'b',
         'a', 'b', 'd', 'b', 'd', 'b', '$', 'b'],
        ['ao', 'o', 'aa', 'o', 'aa', 'o', 'ao', 'o',
         'ao', 'o', 'ia', 'o', 'ia', 'o', '', 'o'],
        [-2, -1, -2, -1, -2, -1, -2, -1, -2, -1, -2, -1, -2, -1, 0, -1],
    )
    assert get_rhymes(
        stressed_endings, assonance=True, relaxation=True,
        unrhymed_verse_symbol="$"
    ) == output


def test_get_rhymes_offset_unrhymed(stressed_endings):
    output = (
        ['$', 'a', '$', 'a', '$', 'a', '$', '$',
         '$', '$', '$', 'b', '$', 'a', '$', 'b'],
        ['', 'or', '', 'or', '', 'or', '', '',
         '', '', '', 'on', '', 'or', '', 'on'],
        [0, -2, 0, -2, 0, -2, 0, 0, 0, 0, 0, -2, 0, -2, 0, -2],
    )
    assert get_rhymes(
        stressed_endings, offset=4, unrhymed_verse_symbol="$"
    ) == output


def test_get_rhymes_assonance_offset_unrhymed(stressed_endings):
    output = (
        ['$', 'a', '$', 'a', '$', 'a', 'b', 'a',
         'b', '$', 'c', 'a', 'c', 'a', '$', 'a'],
        ['', 'o', '', 'o', '', 'o', 'ao', 'o',
         'ao', '', 'ia', 'o', 'ia', 'o', '', 'o'],
        [0, -1, 0, -1, 0, -1, -2, -1, -2, 0, -2, -1, -2, -1, 0, -1],
    )
    assert get_rhymes(
        stressed_endings, assonance=True, offset=4, unrhymed_verse_symbol="$"
    ) == output


def test_get_rhymes_relaxation_offset_unrhymed(stressed_endings):
    output = (
        ['$', 'a', '$', 'a', '$', 'a', '$', '$',
         '$', 'b', '$', 'b', '$', 'a', '$', 'b'],
        ['', 'or', '', 'or', '', 'or', '', '',
         '', 'on', '', 'on', '', 'or', '', 'on'],
        [0, -2, 0, -2, 0, -2, 0, 0, 0, -2, 0, -2, 0, -2, 0, -2],
    )
    assert get_rhymes(
        stressed_endings, relaxation=True, offset=4, unrhymed_verse_symbol="$"
    ) == output


def test_get_rhymes_assonance_relaxation_offset_unrhymed(stressed_endings):
    output = (
        ['$', 'a', 'b', 'a', 'b', 'a', 'c', 'a',
         'c', 'a', 'd', 'a', 'd', 'a', '$', 'a'],
        ['', 'o', 'aa', 'o', 'aa', 'o', 'ao', 'o',
         'ao', 'o', 'ia', 'o', 'ia', 'o', '', 'o'],
        [0, -1, -2, -1, -2, -1, -2, -1, -2, -1, -2, -1, -2, -1, 0, -1],
    )
    assert get_rhymes(
        stressed_endings, assonance=True, relaxation=True, offset=4,
        unrhymed_verse_symbol="$"
    ) == output


def test_search_structure():
    rhymes = 'abcbcbababdbdb-b'
    syllables_count = [9, 7, 8, 8, 8, 8, 8, 7, 8, 8, 9, 7, 9, 8, 9, 7]
    key = "assonant"
    assert STRUCTURES[search_structure(
        rhymes, syllables_count, key
    )][1] == 'romance'  # the romance structure is not defined very rigidly


def test_analyze_rhyme_haiku(haiku):
    """
    Noche sin luna.
    La tempestad estruja
    los viejos cedros.
    """
    assert analyze_rhyme(haiku)["name"] == 'haiku'


def test_analyze_rhyme_sonnet(sonnet):
    """
    La lluvia en el cristal de la ventana,
    el aire de una plaza compartida,
    el pañuelo de sombras de la vida,
    la noche de Madrid y su mañana,
    el amor, la ilusión del porvenir,
    el dolor, la verdad de lo perdido,
    la constancia de un sueño decidido,
    la humana libertad de decidir,
    la prisa, la política, el mercado,
    las noticias, la voz, el indiscreto
    deseo de saber lo silenciado,
    el rumor, las mentiras y el secreto,
    todo lo que la muerte os ha quitado
    quisiera devolverlo en un soneto.
    """
    assert analyze_rhyme(sonnet)["name"] == 'sonnet'


def test_analyze_rhyme_couplet(couplet):
    """
    Aunque la mona se vista de seda,
    mona se queda.
    """
    assert analyze_rhyme(couplet)["name"] == 'couplet'


def test_analyze_rhyme_romance(romance):
    """
    Que por mayo era por mayo,
    cuando hace la calor,
    cuando los trigos encañan
    y están los campos en flor,
    cuando canta la calandria
    y responde el ruiseñor,
    cuando los enamorados
    van a servir al amor;
    sino yo, triste, cuitado,
    que vivo en esta prisión;
    que ni sé cuando es de día
    ni cuando las noches son,
    sino por una avecilla
    que me cantaba al albor.
    Matómela un ballestero;
    déle Dios mal galardón.
    """
    assert analyze_rhyme(romance)["name"] == 'romance'
