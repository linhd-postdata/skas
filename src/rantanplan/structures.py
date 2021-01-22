import itertools
import re

# Stanza structures where each tuple is defined as follows:
# (
#     CONSONANT_RHYME | ASSONANT_RHYME,
#     "structure name",
#     r".*",  # regular expression to match the rhymed line pattern
#     lambda lengths: True  # function checking a condition on line lengths
# )
# Structures will be checked in order of definition, the first one to match
# will be chosen.
ASSONANT_RHYME = "assonant"
CONSONANT_RHYME = "consonant"
ARTE_MAYOR_MIN_LENGTH = 9
ARTE_MENOR_MAX_LENGTH = 8
COPLA_ARTE_MENOR_MIN_LENGTH = 4
LIRA_LONG_LINE = 11
LIRA_SHORT_LINE = 7
SILVA_LONG_LINE = LIRA_LONG_LINE
SILVA_SHORT_LINE = LIRA_SHORT_LINE
HENDECASYLLABLE = 11
ALEXANDRINE = 14
OCTOSYLLABLE = ARTE_MENOR_MAX_LENGTH
TETRASYLLABLE = COPLA_ARTE_MENOR_MIN_LENGTH
MINIMUM_SAFE_LENGTH = 3
MAXIMUM_SAFE_LENGTH = 20
#    STRUCTURES_LENGTH is a dictionary with a list of line lengths and a `True`
#    or `False` flag to indicate if the structure can be repeated or not
STRUCTURES_LENGTH = {
    "seguidilla_compuesta": ([7, 5, 7, 5, 5, 7, 5], False),
    "seguidilla": ([7, 5, 7, 5], False),
    "chamberga": ([7, 5, 7, 5, 3, 7, 3, 7, 3, 7], False),
    "seguidilla_gitana": ([6, 6, 11, 6], False),
    "estrofa_sáfica": ([11, 11, 11, 5], False),
    "estrofa_sáfica_unamuno": ([11, 11, 7, 5], False),
    "estrofa_francisco_de_la_torre": ([11, 11, 11, 7], False),
    "endecha_real": ([7, 7, 7, 11], True),
    "lira": ([7, 11, 7, 7, 11], False),
    "estrofa_manriqueña": ([8, 8, 4, 8, 8, 4], True),
    "ovillejo_tetra": ([8, 4, 8, 4, 8, 4, 8, 8, 8, 8], False),
    "ovillejo_tri": ([8, 3, 8, 3, 8, 3, 8, 8, 8, 8], False),
    "haiku": ([5, 7, 5], False),
    "sonnet": (14*[11], False),
    "soleá": (3*[8], False),
    "romance": ([8, 8], True),
    "copla_real": (10*[8], False),
    "espinela": (10*[8], False),
    "copla_castellana": (8*[8], False),
    "octava_real": (8*[11], False),
    "cuaderna_vía": (4*[14], False),
    "sexta_rima": (6*[11], False),
}


def has_minimum_length(min_length, ranges_list):
    """Checks if every range within a list of ranges contains a minimum length

    :param min_length: Minimum length
    :param ranges_list: List of verse length ranges
    :return:
    """
    return all(min_length <= max(length_range) for length_range in ranges_list)


def has_maximum_length(max_length, ranges_list):
    """Checks if every range within a list of ranges contains a maximum length

    :param max_length: Maximum length
    :param ranges_list: List of verse length ranges
    :return: `True` if all verses pass the condition, `False` otherwise
    """
    return all(max_length >= min(length_range) for length_range in ranges_list)


def has_fixed_length_verses(structure_name, ranges_list, fluctuation_size=0):
    """Checks if a range within a list of ranges contains the respective value
    of a list of lengths, with possible length fluctuation

    :param structure_name: Name of the structure to be checked
    :param ranges_list: List of verse length ranges

    :param fluctuation_size: How much fluctuation is allowed on verse length
    :return: `True` if all verses pass the condition, `False` otherwise
    """
    lengths_list, _ = STRUCTURES_LENGTH[structure_name]
    if len(ranges_list) % len(lengths_list):
        return False
    lengths_list = itertools.cycle(lengths_list)
    if fluctuation_size > 0:
        return all(
            any(length in verse_range
                for length in range(verse_length - fluctuation_size,
                                    verse_length + fluctuation_size + 1))
            for verse_length, verse_range in zip(lengths_list, ranges_list))
    return all(
        map(lambda verse_length, verse_range: verse_length in verse_range,
            lengths_list, ranges_list))


def has_same_length_verses(fixed_length, ranges_list):
    """Checks if all ranges contain the same fixed value

    :param fixed_length: Fixed value to be checked
    :param ranges_list: List of verse length ranges
    :return: `True` if all verses pass the condition, `False` otherwise
    """
    return all(fixed_length in length_range for length_range in ranges_list)


def has_mixed_length_verses(length_a, length_b, ranges_list):
    """Given two numbers, checks whether all ranges contain both of them,
    and only those numbers, at least once.
    This function generates two binary numbers, one for each length,
    with `1` indicating the number is found within a given position in the
    range, and `0` when not found.
    After that, a logical `OR` is applied between the two numbers and the
    output is compared with a binary number with just `1`'s and the length of
    the original list of ranges.

    For example:
    length_a: 011001
    length_b: 101001

    Both numbers are greater than one so that means at least one of each length
    has been found and we proceed to calculate the `OR` output

    length_a:    011101
    length_b:    101011  OR
                 ------
    result       111111

    111111 is the same as the expected output 111111 so the condition evaluates
    as `True`

    :param length_a: First length to be checked
    :param length_b: Second length to be checked

    :param ranges_list: List of verse length ranges
    :return: `True` if all verses pass the condition, `False` otherwise
    """
    contains_a = 0
    contains_b = 0
    for (index, interval) in enumerate(ranges_list):
        found_short = length_a in interval
        found_long = length_b in interval
        if not found_short and not found_long:
            # Early termination
            return False
        if found_short:
            contains_a |= 1 << index
        if found_long:
            contains_b |= 1 << index
    return (contains_a > 0) and (
            contains_b > 0) and (
            contains_a | contains_b == (1 << len(ranges_list)) - 1)


def get_rhyme_pattern_counts(string):
    """Count how many times does a character occur in a given string before its
    own position.

    :param string: String with the rhyme pattern
    :return: A string with the count values
    """
    count_dict = {}
    output = []
    for character in string:
        count = count_dict.get(character, 0)
        output.append(count)
        count_dict[character] = count + 1
    return output


def is_terceto_encadenado(rhyme_pattern):
    """Checks if a poem has a structure that matches with "terceto encadenado"

    :param rhyme_pattern: String with the rhyme pattern
    :return: `True` if it matches, `False` otherwise
    """
    string_pattern = [str(c) for c in get_rhyme_pattern_counts(rhyme_pattern)]
    rhyme_pattern_count = "".join(string_pattern)
    return bool(re.match(r"^001(102)*(101(1)?|102)$", rhyme_pattern_count))


STRUCTURES = (
    (
        CONSONANT_RHYME,
        "seguidilla",
        r"(-a-a)|(abab)",
        lambda ranges_list: has_fixed_length_verses("seguidilla", ranges_list,
                                                    fluctuation_size=1)
    ), (
        ASSONANT_RHYME,
        "seguidilla",
        r"(-a-a)|(abab)",
        lambda ranges_list: has_fixed_length_verses("seguidilla", ranges_list,
                                                    fluctuation_size=1)
    ), (
        CONSONANT_RHYME,
        "seguidilla_compuesta",
        r"((a-a-)|(-a-a)|(abab))((a-a)|(b-b)|(c-c))",
        lambda ranges_list: has_fixed_length_verses("seguidilla_compuesta",
                                                    ranges_list)
    ), (
        ASSONANT_RHYME,
        "seguidilla_compuesta",
        r"((a-a-)|(-a-a)|(abab))((a-a)|(b-b)|(c-c))",
        lambda ranges_list: has_fixed_length_verses("seguidilla_compuesta",
                                                    ranges_list)
    ), (
        ASSONANT_RHYME,
        "chamberga",
        r"(([^a]a[^a]a)|(abab)|[^a]a[^a]a)([^-]{2}){3}",
        lambda ranges_list: has_fixed_length_verses("chamberga", ranges_list)
    ), (
        ASSONANT_RHYME,
        "seguidilla_gitana",
        r"(-a-a)|(a-a-)",
        lambda ranges_list: has_fixed_length_verses("seguidilla_gitana", ranges_list)
    ), (
        ASSONANT_RHYME,
        "endecha_real",
        r"(-a-a){1,}",
        lambda ranges_list: has_fixed_length_verses("endecha_real", ranges_list)
    ), (
        CONSONANT_RHYME,
        "cuarteto_lira",
        r"(abab)|(abba)|(-a-a)",
        lambda ranges_list: has_mixed_length_verses(LIRA_LONG_LINE, LIRA_SHORT_LINE,
                                                    ranges_list)
    ), (
        ASSONANT_RHYME,
        "cuarteto_lira",
        r"(abab)|(abba)|(-a-a)",
        lambda ranges_list: has_mixed_length_verses(LIRA_LONG_LINE, LIRA_SHORT_LINE,
                                                    ranges_list)
    ), (
        CONSONANT_RHYME,
        "estrofa_sáfica_unamuno",  # se puede encadenar?
        r"(----)|(a-a-)|(ab-b)|(abab)",
        lambda ranges_list: has_fixed_length_verses("estrofa_sáfica_unamuno",
                                                    ranges_list)
    ), (
        ASSONANT_RHYME,
        "estrofa_sáfica",  # se puede encadenar?
        r"(----)|(a-a-)|(ab-b)|(abab)",
        lambda ranges_list: has_fixed_length_verses("estrofa_sáfica", ranges_list)
    ), (
        CONSONANT_RHYME,
        "estrofa_francisco_de_la_torre",
        r"(----)|(a-a-)",
        lambda ranges_list: has_fixed_length_verses(
            "estrofa_francisco_de_la_torre", ranges_list)
    ), (
        ASSONANT_RHYME,
        "estrofa_francisco_de_la_torre",
        r"(----)|(a-a-)",
        lambda ranges_list: has_fixed_length_verses(
            "estrofa_francisco_de_la_torre", ranges_list)
    ), (
        CONSONANT_RHYME,
        "estrofa_manriqueña",
        r"abcabc|abcabcdefdef",
        lambda ranges_list: has_fixed_length_verses("estrofa_manriqueña",
                                                    ranges_list,
                                                    fluctuation_size=1)
    ), (
        CONSONANT_RHYME,
        "sextilla",
        r"aabaab|abcabc|ababab|abbccb|aababa|aabccb|-aabba",
        lambda ranges_list: (
            has_maximum_length(ARTE_MENOR_MAX_LENGTH,
                               ranges_list)
        ) or (
            has_mixed_length_verses(OCTOSYLLABLE,
                                    TETRASYLLABLE,
                                    ranges_list)
        )
    ), (
        CONSONANT_RHYME,
        "sexteto_lira",
        r"ababcc|aabccb|abcabc|abbacc",
        lambda ranges_list: has_mixed_length_verses(LIRA_LONG_LINE, LIRA_SHORT_LINE,
                                                    ranges_list)
    ), (
        CONSONANT_RHYME,
        "septeto_lira",
        r"ababbcc|abcabcc",
        lambda ranges_list: has_mixed_length_verses(LIRA_LONG_LINE, LIRA_SHORT_LINE,
                                                    ranges_list)
    ), (
        CONSONANT_RHYME,
        "ovillejo",
        r"aabbcccddc",
        lambda ranges_list: (
            has_fixed_length_verses("ovillejo_tetra", ranges_list,
                                    fluctuation_size=1)
        ) or (
            has_fixed_length_verses("ovillejo_tri", ranges_list,
                                    fluctuation_size=1)
        )
    ), (
        CONSONANT_RHYME,
        "sonnet",
        r"(abba|abab|cddc|cdcd){2}((cd|ef){3}|(cde|efg){2}|[cde]{6})",
        lambda ranges_list: has_minimum_length(ARTE_MAYOR_MIN_LENGTH, ranges_list)
    ), (
        CONSONANT_RHYME,
        "couplet",
        r"aa",
        lambda ranges_list: (
                            has_maximum_length(MAXIMUM_SAFE_LENGTH, ranges_list)
                             ) and (
                            has_minimum_length(MINIMUM_SAFE_LENGTH, ranges_list)
        )
    ), (
        CONSONANT_RHYME,
        "tercetillo",
        r"a.a",
        lambda ranges_list: has_maximum_length(ARTE_MENOR_MAX_LENGTH, ranges_list)
    ), (
        CONSONANT_RHYME,
        "terceto_monorrimo",
        r"aaa",
        lambda ranges_list: has_minimum_length(ARTE_MAYOR_MIN_LENGTH, ranges_list)
    ), (
        CONSONANT_RHYME,
        "terceto",
        r"(a-a)|(-aa)|(aa-)",
        lambda ranges_list: has_minimum_length(ARTE_MAYOR_MIN_LENGTH, ranges_list)
    ), (
        CONSONANT_RHYME,
        "sexta_rima",
        r"ababcc|aabccb|aabcbc",
        lambda ranges_list: has_fixed_length_verses("sexta_rima", ranges_list)
    ), (
        CONSONANT_RHYME,
        "sexteto",
        r"aabccb|aababa|-aabba|ababab|abcabc|.{6}",
        lambda ranges_list: has_minimum_length(ARTE_MAYOR_MIN_LENGTH, ranges_list)
    ), (
        CONSONANT_RHYME,
        "redondilla",
        r"abba",
        lambda ranges_list: has_maximum_length(ARTE_MENOR_MAX_LENGTH, ranges_list)
    ), (
        ASSONANT_RHYME,
        "redondilla",
        r"abba",
        lambda ranges_list: has_maximum_length(ARTE_MENOR_MAX_LENGTH, ranges_list)
    ), (
        CONSONANT_RHYME,
        "cuarteto",
        r"abba",
        lambda ranges_list: has_minimum_length(ARTE_MAYOR_MIN_LENGTH, ranges_list)
    ), (
        CONSONANT_RHYME,
        "cuarteta",
        r"abab",
        lambda ranges_list: has_maximum_length(ARTE_MENOR_MAX_LENGTH, ranges_list)
    ), (
        CONSONANT_RHYME,
        "serventesio",
        r"abab",
        lambda ranges_list: has_minimum_length(ARTE_MAYOR_MIN_LENGTH, ranges_list)
    ), (
        CONSONANT_RHYME,
        "cuaderna_vía",
        r"aaaa",
        lambda ranges_list: has_fixed_length_verses("cuaderna_vía", ranges_list)
    ), (
        CONSONANT_RHYME,
        "octava_real",
        r"(abababcc)",
        lambda ranges_list: has_fixed_length_verses("octava_real", ranges_list)
    ), (
        CONSONANT_RHYME,
        "copla_arte_mayor",
        r"(abbaacca)|(ababbccb)|(abbaacac)",
        lambda ranges_list: has_minimum_length(ARTE_MAYOR_MIN_LENGTH,
                                               ranges_list)
        and not (
            has_maximum_length(ARTE_MENOR_MAX_LENGTH, ranges_list)
        )
    ), (
        CONSONANT_RHYME,
        "copla_mixta",
        r"abbacca",
        lambda ranges_list: has_maximum_length(ARTE_MENOR_MAX_LENGTH, ranges_list)
    ), (
        CONSONANT_RHYME,
        "octavilla",
        r"(abbecdde)|(ababbccb)|(-aab-ccb)|(abbcaddc)",
        lambda ranges_list: has_maximum_length(ARTE_MENOR_MAX_LENGTH, ranges_list)
    ), (
        ASSONANT_RHYME,
        "octavilla",
        r"(abbecdde)|(ababbccb)|(-aab-ccb)",
        lambda ranges_list: has_maximum_length(ARTE_MENOR_MAX_LENGTH, ranges_list)
    ), (
        CONSONANT_RHYME,
        "terceto_encadenado",
        is_terceto_encadenado,
        lambda ranges_list: has_minimum_length(ARTE_MAYOR_MIN_LENGTH, ranges_list)
    ), (
        CONSONANT_RHYME,
        "copla_arte_menor",
        r"abbaacca|ababbccb|abbaacac|ababacca|abbaabba",
        lambda ranges_list: (
            has_maximum_length(ARTE_MENOR_MAX_LENGTH, ranges_list)
        ) or (
            has_mixed_length_verses(OCTOSYLLABLE, TETRASYLLABLE, ranges_list)
        )
    ), (
        CONSONANT_RHYME,
        "copla_castellana",
        r"(abbacddc)|(ababcdcd)|(abbacdcd)|(ababcddc)|(abbaacca)",
        lambda ranges_list: (
            has_same_length_verses(OCTOSYLLABLE, ranges_list)
        ) or (
            has_mixed_length_verses(OCTOSYLLABLE, TETRASYLLABLE, ranges_list)
        )
    ), (
        CONSONANT_RHYME,
        "octava",
        r".{8}",
        lambda ranges_list: (
            has_minimum_length(ARTE_MAYOR_MIN_LENGTH, ranges_list)
        ) or (
            has_maximum_length(ARTE_MENOR_MAX_LENGTH, ranges_list)
        )
    ), (
        ASSONANT_RHYME,
        "octava",
        r".{8}",
        lambda ranges_list: (
            has_minimum_length(ARTE_MAYOR_MIN_LENGTH, ranges_list)
        ) or (
            has_maximum_length(ARTE_MENOR_MAX_LENGTH, ranges_list)
        )
    ), (
        CONSONANT_RHYME,
        "espinela",
        r"abbaaccddc",
        lambda ranges_list: has_fixed_length_verses("espinela", ranges_list)
    ), (
        CONSONANT_RHYME,
        "copla_real",
        r"""((ababa)|(abaab)|(abbab)|(aabab)|(aabba))
        ((ababa)|(abaab)|(abbab)|(aabab)|(aabba)
        (cdcdc)|(cdccd)|(cddcd)|(ccdcd)|(ccddc))""",
        # tiene versos quebrados, cambiar regla de ranges_list?
        lambda ranges_list: (
            has_fixed_length_verses("copla_real",
                                    ranges_list)
        ) or (
            has_same_length_verses(OCTOSYLLABLE,
                                   ranges_list)
        )
    ), (
        CONSONANT_RHYME,
        "lira",
        r"ababb",
        lambda ranges_list: has_fixed_length_verses("lira", ranges_list)
    ), (
        CONSONANT_RHYME,
        "quinteto",
        r"(ababa|abaab|abbab|aabab|aabba)",
        lambda ranges_list: has_minimum_length(ARTE_MAYOR_MIN_LENGTH, ranges_list)
    ), (
        CONSONANT_RHYME,
        "quintilla",
        r"(ababa|abaab|abbab|aabab|aabba)",
        lambda ranges_list: has_maximum_length(ARTE_MENOR_MAX_LENGTH, ranges_list)
    ), (
        ASSONANT_RHYME,
        "couplet",
        r"aa",
        lambda ranges_list: (
                has_maximum_length(MAXIMUM_SAFE_LENGTH, ranges_list)
                and has_minimum_length(MINIMUM_SAFE_LENGTH, ranges_list))
    ), (
        ASSONANT_RHYME,
        "silva_arromanzada",
        r"(([^a]a)+)|([^b]b)+",
        lambda ranges_list: has_mixed_length_verses(SILVA_LONG_LINE,
                                                    SILVA_SHORT_LINE,
                                                    ranges_list)
    ), (
        ASSONANT_RHYME,
        "cantar",
        r"-a-a",
        lambda ranges_list: has_maximum_length(ARTE_MENOR_MAX_LENGTH, ranges_list)
    ), (
        ASSONANT_RHYME,
        "romance",
        r"((.b)+)|(([^a]a)+)",
        lambda ranges_list: has_fixed_length_verses("romance", ranges_list)
    ), (
        ASSONANT_RHYME,
        "romance_arte_mayor",
        r"((.b)+)|(([^a]a)+)",
        lambda ranges_list: has_minimum_length(ARTE_MAYOR_MIN_LENGTH, ranges_list)
    ), (
        ASSONANT_RHYME,
        "haiku",
        r".*",
        lambda ranges_list: has_fixed_length_verses("haiku", ranges_list)
    ), (
        ASSONANT_RHYME,
        "soleá",
        r"(a-a)",
        lambda ranges_list: has_fixed_length_verses("soleá", ranges_list)
    ), (
        CONSONANT_RHYME,
        "décima_antigua",
        r"""
        abbaacccca|abbaacccaa|abbaacc.c.|abbacddcdd|abaabacdcd|abbacdecde|
        abaabbabab|abaabbcccb|abbaaccaac|abbaabcddc|abbaccaaac|abbaccdddc|
        abbacddcee|abba.cccc.|ababbcbcdd|abaabccaac|ababbacddc|ababcdcdcc|
        abbaacacca|abaabbcbbc
        """,
        lambda ranges_list: (
            has_mixed_length_verses(OCTOSYLLABLE, TETRASYLLABLE, ranges_list)
        ) or (
            has_same_length_verses(OCTOSYLLABLE, ranges_list)
                            )
    ), (
        CONSONANT_RHYME,
        "septilla",
        r".{7}",
        lambda ranges_list: has_maximum_length(ARTE_MENOR_MAX_LENGTH, ranges_list)
    ), (
        CONSONANT_RHYME,
        "septeto",
        r".{7}",
        lambda ranges_list: has_minimum_length(ARTE_MAYOR_MIN_LENGTH, ranges_list)
    ), (
        CONSONANT_RHYME,
        "novena",
        r".{9}",
        lambda _: True
    )
)
