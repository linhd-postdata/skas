from rantanplan.rhymes import assign_letter_codes
from rantanplan.rhymes import get_clean_codes
from rantanplan.rhymes import get_stressed_endings


def test_get_stressed_endings():
    # plátano
    # mano
    # prisión
    lines = [
        {'tokens': [{
            'word': [
                {'syllable': 'plá', 'is_stressed': True},
                {'syllable': 'ta', 'is_stressed': False},
                {'syllable': 'no', 'is_stressed': False}
            ],
            'stress_position': -3}
        ]},
        {'tokens': [{
            'word': [
                {'syllable': 'ma', 'is_stressed': True},
                {'syllable': 'no', 'is_stressed': False}
            ],
            'stress_position': -2}
        ]},
        {'tokens': [{
            'word': [
                {'syllable': 'pri', 'is_stressed': False},
                {'syllable': 'sión', 'is_stressed': True}
            ],
            'stress_position': -1}
        ]}
    ]
    output = [
        (['plá', 'ta', 'no'], 3, -3),
        (['ma', 'no'], 2, -2),
        (['sión'], 2, -1)
    ]
    assert get_stressed_endings(lines) == output


def test_get_clean_codes():
    # Consonant rhyme by default
    stressed_endings = [
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
    output = (
        {0: 'Ayo', 1: 'OR', 2: 'Añan', 3: 'ANdria', 4: 'Ados', 5: 'Ado',
         6: 'ION', 7: 'Ia', 8: 'ON', 9: 'Illa', 10: 'Ero'},
        [0, 1, 2, 1, 3, 1, 4, 1, 5, 6, 7, 8, 9, 1, 10, 8],
        {0, 2, 3, 4, 5, 6, 7, 9, 10},
    )
    assert get_clean_codes(stressed_endings) == output
    assert get_clean_codes(stressed_endings, False, False) == output


def test_get_clean_codes_assonance():
    stressed_endings = [
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
    output = (
        {0: 'Ao', 1: 'O', 2: 'Aa', 3: 'Aia', 4: 'IO', 5: 'Ia', 6: 'Eo'},
        [0, 1, 2, 1, 3, 1, 0, 1, 0, 4, 5, 1, 5, 1, 6, 1],
        {2, 3, 4, 6},
    )
    assert get_clean_codes(stressed_endings, assonance=True) == output
    assert get_clean_codes(stressed_endings, True, False) == output


def test_get_clean_codes_relaxation():
    stressed_endings = [
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
    output = (
        {0: 'Ayo', 1: 'OR', 2: 'Añan', 3: 'ANdra', 4: 'Ados', 5: 'Ado',
         6: 'ON', 7: 'Ia', 8: 'Illa', 9: 'Ero'},
        [0, 1, 2, 1, 3, 1, 4, 1, 5, 6, 7, 6, 8, 1, 9, 6],
        {0, 2, 3, 4, 5, 7, 8, 9},
    )
    assert get_clean_codes(stressed_endings, relaxation=True) == output
    assert get_clean_codes(stressed_endings, False, True) == output


def test_get_clean_codes_assonance_relaxation():
    stressed_endings = [
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
