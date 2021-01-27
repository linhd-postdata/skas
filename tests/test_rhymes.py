# -*- coding: utf-8 -*-
import json
from pathlib import Path

import pytest

from rantanplan.core import get_scansion
from rantanplan.rhymes import analyze_rhyme
from rantanplan.rhymes import apply_offset
from rantanplan.rhymes import assign_letter_codes
from rantanplan.rhymes import get_best_rhyme_candidate
from rantanplan.rhymes import get_clean_codes
from rantanplan.rhymes import get_ending_with_liaison
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


@pytest.fixture
def rhyme_analysis_haiku():
    return json.loads(
        Path("tests/fixtures/rhyme_analysis_haiku.json").read_text())


@pytest.fixture
def rhyme_analysis_sonnet():
    return json.loads(
        Path("tests/fixtures/rhyme_analysis_sonnet.json").read_text())


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
        {
            0: 'Ayo', 1: 'OR', 2: 'Añan', 3: 'ANdria', 4: 'Ados',
            5: 'Ado', 6: 'iOn', 7: 'Ia', 8: 'ON', 9: 'Illa', 10: 'Ero',
            11: 'On'},
        [0, 1, 2, 1, 3, 1, 4, 1, 5, 6, 7, 8, 9, 1, 10, 11]
    )
    assert get_clean_codes(stressed_endings) == output
    assert get_clean_codes(stressed_endings, False, False) == output


def test_get_clean_codes_assonance(stressed_endings):
    output = (
        {
            0: 'Ao', 1: 'O', 2: 'Aa', 3: 'Aia', 4: 'iO', 5: 'Ia', 6: 'Eo'},
        [0, 1, 2, 1, 3, 1, 0, 1, 0, 4, 5, 1, 5, 1, 6, 1]
    )
    assert get_clean_codes(stressed_endings, assonance=True) == output
    assert get_clean_codes(stressed_endings, True, False) == output


def test_get_clean_codes_relaxation(stressed_endings):
    output = (
        ({0: 'Ayo', 1: 'OR', 2: 'Añan', 3: 'ANdra', 4: 'Ados', 5: 'Ado',
          6: 'On', 7: 'Ia', 8: 'ON', 9: 'Iya', 10: 'Ero'},
         [0, 1, 2, 1, 3, 1, 4, 1, 5, 6, 7, 8, 9, 1, 10, 6])
    )
    assert get_clean_codes(stressed_endings, relaxation=True) == output
    assert get_clean_codes(stressed_endings, False, True) == output


def test_get_clean_codes_assonance_relaxation(stressed_endings):
    output = (
        {0: 'Ao', 1: 'O', 2: 'Aa', 3: 'Ia', 4: 'Eo'},
        [0, 1, 2, 1, 2, 1, 0, 1, 0, 1, 3, 1, 3, 1, 4, 1],
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


def test_assign_letter_codes_exceeded_offset():
    clean_codes = (
        {0: 'Aa', 1: 'Oe', 2: 'Ia', 3: 'Oa'},
        [0, 1, 2, 1, 3, 0, 3],
        {2}
    )
    output = (
        [0, 1, -1, 1, 2, 0, 2],
        ['Aa', 'Oe', '', 'Oe', 'Oa', 'Aa', 'Oa']
    )
    assert assign_letter_codes(*clean_codes) == output


def test_sort_rhyme_letters():
    rhymes_codes = [-1, 1, 2, 1, 2, 1, 0, 1, 0, 1, 3, 1, 3, 1, -1, 1]
    output = ['-', 'a', 'b', 'a', 'b', 'a', 'c', 'a',
              'c', 'a', 'd', 'a', 'd', 'a', '-', 'a']
    assert rhyme_codes_to_letters(rhymes_codes) == output


def test_apply_offset():
    codes = {0: 'Oo', 1: 'Ao', 2: 'IEo', 3: 'Aa', 4: 'Uo'}
    code_numbers = [0, 1, 2, 1, 3, 3, 4, 4, 1, 1, 3, 3]
    out = (
        {0: 'Oo', 1: 'Ao', 2: 'IEo', 3: 'Aa', 4: 'Uo', 5: 'Ao', 6: 'Aa'},
        [0, 1, 2, 1, 3, 3, 4, 4, 5, 5, 6, 6]
    )
    assert apply_offset(codes, code_numbers) == out


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
        ['-', 'a', '-', 'a', '-', 'a', '-', 'a', '-', '-', '-', '-', '-', 'a',
         '-', '-'],
        ['', 'or', '', 'or', '', 'or', '', 'or', '', '', '', '', '', 'or', '',
         ''],
        [0, -2, 0, -2, 0, -2, 0, -2, 0, 0, 0, 0, 0, -2, 0, 0]
    )
    assert get_rhymes(stressed_endings) == output


def test_get_rhymes_assonance(stressed_endings):
    output = (
        ['a', 'b', '-', 'b', '-', 'b', 'a', 'b',
         'a', '-', 'c', 'b', 'c', 'b', '-', 'b'],
        ['ao', 'o', '', 'o', '', 'o', 'ao', 'o',
         'ao', '', 'ia', 'o', 'ia', 'o', '', 'o'],
        [-2, -1, 0, -1, 0, -1, -2, -1, -2, 0, -2, -1, -2, -1, 0, -1],
    )
    assert get_rhymes(stressed_endings, assonance=True) == output


def test_get_rhymes_relaxation(stressed_endings):
    output = (
        ['-', 'a', '-', 'a', '-', 'a', '-', 'a', '-', 'b', '-', '-', '-', 'a',
         '-', 'b'],
        ['', 'or', '', 'or', '', 'or', '', 'or', '', 'on', '', '', '', 'or',
         '', 'on'], [0, -2, 0, -2, 0, -2, 0, -2, 0, -2, 0, 0, 0, -2, 0, -2]
    )
    assert get_rhymes(stressed_endings, relaxation=True) == output


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
        ['-', 'a', '-', 'a', '-', 'a', '-', 'a', '-', '-', '-', '-',
         '-', '-', '-', '-'],
        ['', 'or', '', 'or', '', 'or', '', 'or', '', '', '', '', '',
         '', '', ''],
        [0, -2, 0, -2, 0, -2, 0, -2, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    assert get_rhymes(stressed_endings, offset=4) == output


def test_get_rhymes_assonance_offset(stressed_endings):
    output = (
        ['-', 'a', '-', 'a', '-', 'a', 'b', 'a', 'b', '-', 'c', 'a', 'c', 'a',
         '-', 'a'],
        ['', 'o', '', 'o', '', 'o', 'ao', 'o', 'ao', '', 'ia', 'o', 'ia', 'o',
         '', 'o'],
        [0, -1, 0, -1, 0, -1, -2, -1, -2, 0, -2, -1, -2, -1, 0, -1]
    )
    assert get_rhymes(
        stressed_endings, assonance=True, offset=4
    ) == output


def test_get_rhymes_relaxation_offset(stressed_endings):
    output = (
        ['-', 'a', '-', 'a', '-', 'a', '-', 'a', '-', '-', '-', '-', '-', '-',
         '-', '-'],
        ['', 'or', '', 'or', '', 'or', '', 'or', '', '', '', '', '', '', '',
         ''],
        [0, -2, 0, -2, 0, -2, 0, -2, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    assert get_rhymes(
        stressed_endings, relaxation=True, offset=4
    ) == output


def test_get_rhymes_assonance_relaxation_offset(stressed_endings):
    output = (
        ['-', 'a', 'b', 'a', 'b', 'a', 'c', 'a', 'c', 'a', 'd', 'a', 'd', 'a',
         '-', 'a'],
        ['', 'o', 'aa', 'o', 'aa', 'o', 'ao', 'o', 'ao', 'o', 'ia', 'o', 'ia',
         'o', '', 'o'],
        [0, -1, -2, -1, -2, -1, -2, -1, -2, -1, -2, -1, -2, -1, 0, -1]
    )
    assert get_rhymes(
        stressed_endings, assonance=True, relaxation=True, offset=4
    ) == output


def test_get_rhymes_unrhymed(stressed_endings):
    output = (
        ['$', 'a', '$', 'a', '$', 'a', '$', 'a', '$', '$', '$', '$', '$', 'a',
         '$', '$'],
        ['', 'or', '', 'or', '', 'or', '', 'or', '', '', '', '', '', 'or', '',
         ''], [0, -2, 0, -2, 0, -2, 0, -2, 0, 0, 0, 0, 0, -2, 0, 0]
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
        ['$', 'a', '$', 'a', '$', 'a', '$', 'a', '$', 'b', '$', '$', '$', 'a',
         '$', 'b'],
        ['', 'or', '', 'or', '', 'or', '', 'or', '', 'on', '', '', '', 'or',
         '', 'on'], [0, -2, 0, -2, 0, -2, 0, -2, 0, -2, 0, 0, 0, -2, 0, -2]
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
        ['$', 'a', '$', 'a', '$', 'a', '$', 'a', '$', '$', '$', '$', '$', '$',
         '$', '$'],
        ['', 'or', '', 'or', '', 'or', '', 'or', '', '', '', '', '', '', '',
         ''],
        [0, -2, 0, -2, 0, -2, 0, -2, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    assert get_rhymes(
        stressed_endings, offset=4, unrhymed_verse_symbol="$"
    ) == output


def test_get_rhymes_assonance_offset_unrhymed(stressed_endings):
    output = (
        ['$', 'a', '$', 'a', '$', 'a', 'b', 'a', 'b', '$', 'c', 'a', 'c', 'a',
         '$', 'a'],
        ['', 'o', '', 'o', '', 'o', 'ao', 'o', 'ao', '', 'ia', 'o', 'ia', 'o',
         '', 'o'],
        [0, -1, 0, -1, 0, -1, -2, -1, -2, 0, -2, -1, -2, -1, 0, -1]
    )
    assert get_rhymes(
        stressed_endings, assonance=True, offset=4, unrhymed_verse_symbol="$"
    ) == output


def test_get_rhymes_relaxation_offset_unrhymed(stressed_endings):
    output = (
        ['$', 'a', '$', 'a', '$', 'a', '$', 'a', '$', '$', '$', '$', '$', '$',
         '$', '$'],
        ['', 'or', '', 'or', '', 'or', '', 'or', '', '', '', '', '', '', '',
         ''],
        [0, -2, 0, -2, 0, -2, 0, -2, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    assert get_rhymes(
        stressed_endings, relaxation=True, offset=4, unrhymed_verse_symbol="$"
    ) == output


def test_get_rhymes_assonance_relaxation_offset_unrhymed(stressed_endings):
    output = (
        ['$', 'a', 'b', 'a', 'b', 'a', 'c', 'a', 'c', 'a', 'd', 'a', 'd', 'a',
         '$', 'a'],
        ['', 'o', 'aa', 'o', 'aa', 'o', 'ao', 'o', 'ao', 'o', 'ia', 'o', 'ia',
         'o', '', 'o'],
        [0, -1, -2, -1, -2, -1, -2, -1, -2, -1, -2, -1, -2, -1, 0, -1]
    )
    assert get_rhymes(
        stressed_endings, assonance=True, relaxation=True, offset=4,
        unrhymed_verse_symbol="$"
    ) == output


def test_get_rhymes_assonance_relaxation_exceeded_offset_unrhymed():
    stressed_endings = [
        (['car', 'cha'], 7, -2),
        (['po', 'bre'], 5, -2),
        (['días'], 6, -1),
        (['no', 'ches'], 5, -2),
        (['bo', 'lla'], 5, -2),
        (['car', 'cha'], 6, -2),
        (['don', 'da'], 5, -2)
    ]
    output = (
        ['-', 'a', '-', 'a', 'b', '-', 'b'],
        ['', 'oe', '', 'oe', 'oa', '', 'oa'],
        [0, -2, 0, -2, -2, 0, -2]
    )
    assert get_rhymes(
        stressed_endings, assonance=True, relaxation=True, offset=4
    ) == output


def test_search_structure():
    rhymes = '-a-a'
    ranges_list = [range(14, 16), range(14, 17), range(12, 15), range(15, 18)]
    key = "assonant"
    assert search_structure(rhymes, ranges_list, key) == [50]


def test_analyze_rhyme_haiku(rhyme_analysis_haiku):
    """
    Noche sin luna.
    La tempestad estruja
    los viejos cedros.
    """
    assert analyze_rhyme(rhyme_analysis_haiku)["name"] == 'haiku'


def test_analyze_rhyme_sonnet(rhyme_analysis_sonnet):
    """
    Cruel amor, ¿tan fieras sinrazones
    tras tanta confusión, tras pena tanta?
    ¿De qué sirve la argolla a la garganta
    a quién jamás huyó de sus prisiones?
    ¿Hierro por premio das a mis pasiones?
    Dueño cruel, tu sinrazón espanta,
    el castigo a la pena se adelanta
    y cuando sirvo bien hierros me pones.
    ¡Gentil laurel, amor; buenos despojos!
    Y en un sujeto a tus mudanzas firme
    hierro, virote, lágrimas y enojos.
    Mas pienso que has querido persuadirme
    que trayendo los hierros a los ojos
    no pueda de la causa arrepentirme.
    """
    assert analyze_rhyme(rhyme_analysis_sonnet)["name"] == 'sonnet'


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


def test_rhyme_analysis_tercetillo_consonant():
    poem = """Poderoso visionario,
    raro ingenio temerario,
    por ti enciendo mi incensario."""
    output = ("tercetillo", "consonant")
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert (input_poem[0]["structure"], input_poem[0]["rhyme_type"]) == output


def test_rhyme_analysis_solea():
    poem = """Poderoso es mi marido,
    raro ingenio temeramos,
    por ti enciendo mi inciensito."""
    output = ("soleá", "assonant")
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert (input_poem[0]["structure"], input_poem[0]["rhyme_type"]) == output


def test_rhyme_analysis_terceto():
    poem = """Cumpliéronse de entrambos los deseos,
    pues ella dio mil glorias a Agustino,
    y él a alumbrarla con su pluma vino."""
    output = "terceto"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_rhyme_analysis_terceto_monorrimo():
    poem = """Y abrillantó a mi espíritu la cumbre
    con fugaz cuanto rica certidumbre,
    como con tintas de refleja lumbre."""
    output = "terceto_monorrimo"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_rhyme_analysis_redondilla_consonant():
    poem = """Cerró la infancia su puerta
    a sus damas y a su tío,
    achacando este desvío
    a una enfermedad incierta."""
    output = ("redondilla", "consonant")
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert (input_poem[0]["structure"], input_poem[0]["rhyme_type"]) == output


def test_rhyme_analysis_redondilla_assonant():
    poem = """Cerró la infancia su pueda
    a sus damas y a su piro,
    achacando este desvino
    a una enfermedad incierta."""
    output = ("redondilla", "assonant")
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert (input_poem[0]["structure"], input_poem[0]["rhyme_type"]) == output


def test_rhyme_analysis_cuarteto():
    poem = """Si (como el griego afirma en el Cratilo)
    el nombre es arquetipo de la cosa,
    en las letras de rosa está la rosa
    y todo el Nilo en la palabra Nilo."""
    output = "cuarteto"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_rhyme_analysis_serventesio():
    poem = """¿Vienes? Me llega aquí, pues que suspiras,
    un soplo de las mágicas fragancias
    que hicieran los delirios de las liras
    en las Grecias, las Romas y las Francias."""
    output = "serventesio"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_rhyme_analysis_cuaderna_via():
    poem = """Mester traigo fermoso non es de juglaría
    mester es sin pecado, ca es de clerecía
    fablar curso rimado por la cuaderna vía
    a sílabas cunctadas, ca es gran maestría."""
    output = "cuaderna_vía"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_rhyme_analysis_cuarteta():
    poem = """Se desgrana un cristal fino
    sobre el sueño de una flor;
    trina el poeta divino...
    ¡Bien trinado, Ruiseñor!"""
    output = "cuarteta"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_rhyme_analysis_octava_real():
    poem = """Bajo la luz plural de los azahares
    y los limones de los limoneros,
    tú, la hortelana de los tres lunares.
    Vas aún sobre un cultivo de luceros.
    páranse, ya sin hilo, los telares
    de los fríos gusanos carceleros,
    presos ya. Y bajo el cuello tus carrillos
    lácteos se enveran dulces ya, amarillos."""
    output = "octava_real"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_rhyme_analysis_copla_arte_mayor():
    poem = """De cándida púrpura su vestidura
    bien denotava su grand señorío;
    non le ponía su fausto más brío,
    nin le privava virtud fermosura:
    vençíase della su ropa en albura;
    el ramo de palma su mano sostiene,
    don que Diana por más rico tiene,
    más mesurada que toda mesura."""
    output = "copla_arte_mayor"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_rhyme_analysis_romance_arte_mayor():
    poem = """Quietud, quietud... Ya la ciudad de oro
    ha entrado en el misterio de la tarde.
    La catedral es un gran relicario.
    La bahía unifica sus cristales
    en un azul de arcaicas mayúsculas
    de los antifonarios y misales.
    Las barcas pescadoras estilizan
    el blancor de sus velas triangulares
    y como un eco que dijera: «Ulises»,
    junta alientos de flores y de sales."""
    output = "romance_arte_mayor"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_rhyme_analysis_espinela():
    poem = """Suele decirme la gente
    que en parte sabe mi mal,
    que la causa principal
    se me ve escrita en la frente;
    y aunque hago de valiente,
    luego mi lengua desliza
    por lo que dora y matiza;
    que lo que el pecho no gasta
    ningún disimulo basta
    a cubrirlo con ceniza."""
    output = "espinela"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_rhyme_copla_real():
    poem = """¡Oh altissima cordura
    a do todo el bien consiste,
    yo llena de hermosura
    de tu divina apostura
    razón digna me heziste;
    yo soy diuina en el cielo
    porque de ti soy mandada;
    yo soy de tan alto vuelo;
    yo soy la que en este suelo
    jamás me conturba nada!"""
    output = "copla_real"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_rhyme_silva_arromanzada():
    poem = """El pensador llegó a la barca negra;
    y le vieron hundirse
    en las brumas del lago del Misterio
    los ojos de los cisnes.
    Su manto de poeta
    reconocieron los ilustres lises
    y el laurel y la espina entremezclados
    sobre la frente triste.
    A lo lejos alzábanse los muros
    de la ciudad teológica, en que vive
    la sempiterna Paz. La negra barca
    llegó a la ansiada costa, y el sublime
    espíritu gozó la suma gracia;
    ¡Montaigne! Núñez vio la cruz erguirse,
    y halló al pie de la sacra Vencedora
    el helado cadáver de la Esfinge."""
    output = "silva_arromanzada"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_rhyme_cantar():
    poem = """Algunos desesperados
    solo se curan con soga;
    otros, con siete palabras:
    la fe se ha puesto de moda."""
    output = "cantar"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_rhyme_lira():
    poem = """Si de mi baja lira
    tanto pudiese el son que en un momento
    aplacase la ira
    del animoso viento
    y la furia del mar y el movimiento."""
    output = "lira"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_get_stressed_endings_sinalepha():
    # aplacase la ira
    lines = [
        {'tokens': [
            {'word': [
                {'syllable': 'a', 'is_stressed': False},
                {'syllable': 'pla', 'is_stressed': False},
                {'syllable': 'ca', 'is_stressed': True},
                {'syllable': 'se', 'is_stressed': False,
                 'is_word_end': True}],
                'stress_position': -2},
            {'word': [
                {'syllable': 'la',
                 'is_stressed': False,
                 'has_synalepha': True,
                 'is_word_end': True}],
                'stress_position': 0},
            {'word': [
                {'syllable': 'i', 'is_stressed': True},
                {'syllable': 'ra', 'is_stressed': False,
                 'is_word_end': True}],
                'stress_position': -2}],
            'phonological_groups': [
                {'syllable': 'a', 'is_stressed': False},
                {'syllable': 'pla', 'is_stressed': False},
                {'syllable': 'ca', 'is_stressed': True},
                {'syllable': 'se', 'is_stressed': False,
                 'is_word_end': True},
                {'syllable': 'lai', 'is_stressed': True,
                 'synalepha_index': [1]},
                {'syllable': 'ra', 'is_stressed': False,
                 'is_word_end': True}],
            'rhythm': {'stress': '--+-+-', 'type': 'pattern', 'length': 6}}
    ]
    output = [
        (["i", "ra"], 6, -2)
    ]
    assert get_stressed_endings(lines) == output


def test_get_stressed_endings_synalepha_stressed_vowels():
    lines = [
        {'tokens': [
            {'word': [
                {'syllable': 'A', 'is_stressed': False},
                {'syllable': 'yer', 'is_stressed': True,
                 'is_word_end': True}],
                'stress_position': -1}, {
                'word': [
                    {'syllable': 'so', 'is_stressed': False},
                    {'syllable': 'ñé', 'is_stressed': True,
                     'is_word_end': True}],
                'stress_position': -1}, {
                'word': [
                    {'syllable': 'que', 'is_stressed': False,
                     'is_word_end': True}],
                'stress_position': 0}, {
                'word': [
                    {'syllable': 've', 'is_stressed': False,
                     'has_sinaeresis': True},
                    {'syllable': 'í', 'is_stressed': True,
                     'has_sinaeresis': True},
                    {'syllable': 'a', 'is_stressed': False,
                     'is_word_end': True}],
                'stress_position': -2}],
            'phonological_groups': [
                {'syllable': 'A', 'is_stressed': False},
                {'syllable': 'yer', 'is_stressed': True,
                 'is_word_end': True},
                {'syllable': 'so', 'is_stressed': False},
                {'syllable': 'ñé', 'is_stressed': True,
                 'is_word_end': True},
                {'syllable': 'que', 'is_stressed': False,
                 'is_word_end': True},
                {'syllable': 'veía', 'is_stressed': True,
                 'sinaeresis_index': [1, 2],
                 'is_word_end': True}],
            'rhythm': {'stress': '-+-+-+-', 'type': 'pattern', 'length': 7,
                       'length_range': {'min_length': 7, 'max_length': 9}}}, {
            'tokens': [
                {'word': [
                    {'syllable': 'y', 'is_stressed': False,
                     'is_word_end': True}],
                    'stress_position': 0}, {
                    'word': [
                        {'syllable': 'so', 'is_stressed': False},
                        {'syllable': 'ñé', 'is_stressed': True,
                         'is_word_end': True}], 'stress_position': -1},
                {'word': [
                    {'syllable': 'que', 'is_stressed': False,
                     'is_word_end': True}], 'stress_position': 0},
                {'word': [
                    {'syllable': 'Dios', 'is_stressed': True,
                     'is_word_end': True}], 'stress_position': -1},
                {'word': [
                    {'syllable': 'me', 'is_stressed': False,
                     'has_synalepha': True, 'is_word_end': True}],
                    'stress_position': 0},
                {'word': [
                    {'syllable': 'o', 'is_stressed': False,
                     'has_sinaeresis': True},
                    {'syllable': 'í', 'is_stressed': True,
                     'has_sinaeresis': True},
                    {'syllable': 'a', 'is_stressed': False,
                     'is_word_end': True}],
                    'stress_position': -2}, {'symbol': '...'}],
            'phonological_groups': [
                {'syllable': 'y', 'is_stressed': False,
                 'is_word_end': True},
                {'syllable': 'so',
                 'is_stressed': False},
                {'syllable': 'ñé', 'is_stressed': True,
                 'is_word_end': True},
                {'syllable': 'que',
                 'is_stressed': False,
                 'is_word_end': True},
                {'syllable': 'Dios',
                 'is_stressed': True,
                 'is_word_end': True},
                {'syllable': 'meoía',
                 'is_stressed': True,
                 'synalepha_index': [1],
                 'is_word_end': True}],
            'rhythm': {'stress': '--+-++-', 'type': 'pattern', 'length': 7,
                       'length_range': {'min_length': 7,
                                        'max_length': 8}}}
    ]
    output = [(['ía'], 6, -1), (['ía'], 6, -1)]
    assert get_stressed_endings(lines) == output


def test_get_ending_with_liaison_sinaeresis():
    phonological_group = {'syllable': 'veía', 'is_stressed': True,
                          'sinaeresis_index': [1, 2], 'is_word_end': True}
    liaison = "sinaeresis"
    output = "ía"
    assert get_ending_with_liaison(phonological_group, liaison) == output


def test_get_ending_with_liaison_synalepha():
    phonological_group = {'syllable': 'veía', 'is_stressed': True,
                          'sinaeresis_index': [1, 2], 'is_word_end': True}
    liaison = "synalepha"
    output = "ía"
    assert get_ending_with_liaison(phonological_group, liaison) == output


def test_get_best_rhyme_candidate():
    """Siempre en octubre comenzaba el año.
    ¡Y cuántas veces esa luz de otoño
    me recordó a Fray Luis:
    «Ya el tiempo nos convida
    A los estudios tacaños...»!"""
    candidates = [
        {'rhyme': ['-', '-', '-', '-', '-'], 'endings': ['', '', '', '', ''],
         'endings_stress': [0, 0, 0, 0, 0], 'rhyme_type': 'consonant',
         'rhyme_relaxation': True},
        {'rhyme': ['-', '-', '-', '-', '-'], 'endings': ['', '', '', '', ''],
         'endings_stress': [0, 0, 0, 0, 0], 'rhyme_type': 'consonant',
         'rhyme_relaxation': False},
        {'rhyme': ['a', '-', '-', '-', 'a'],
         'endings': ['ao', '', '', '', 'ao'],
         'endings_stress': [-2, 0, 0, 0, -2],
         'rhyme_type': 'assonant',
         'rhyme_relaxation': True},
        {'rhyme': ['a', '-', '-', '-', 'a'],
         'endings': ['ao', '', '', '', 'ao'],
         'endings_stress': [-2, 0, 0, 0, -2], 'rhyme_type': 'assonant',
         'rhyme_relaxation': False}]
    assert get_best_rhyme_candidate(candidates) == candidates[2]
