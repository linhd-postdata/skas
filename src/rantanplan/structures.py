import re
import statistics
from collections import Counter

# Stanza structures where each tuple is defined as follows:
# (
#     CONSONANT_RHYME | ASSONANT_RHYME,
#     "structure name",
#     r".*",  # regular expression to match the rhymed line pattern
#     lambda lengths: True  # function checking a condition on line lengths
# )
# Structures will be checked in order of definition, the first one to match
# will be chosen.


def most_common_lengths(lengths_list, n=4, number_of_verses=None):
    """Return the n most commons lengths in a list of verses lengths

    :param lengths_list: List with the lengths to be checked
    :param n: Number of most common lengths to be returned
    :param number_of_verses: How many verses are in a given stanza
    :return: The n most common lengths
    """
    most_common_lengths_list = []
    if len(lengths_list) == number_of_verses or number_of_verses is None:
        count = Counter(lengths_list).most_common(n)
        for length, _ in count:
            # `lengths` is a tuple with the length and it's count so we only get
            # the first element of the tuple
            most_common_lengths_list.append(length)
    return most_common_lengths_list


def is_seguidilla_compuesta(lengths):
    """
    [7, 5, 7, 5, 5, 7, 5]
    :param lengths:
    :return:
    """
    correct_lines = 0
    number_of_verses = len(lengths)
    if number_of_verses == 7:
        for i in (0, 2, 5):
            if 9 > lengths[i] > 5:
                correct_lines += 1
        for i in (1, 3, 4, 6):
            if 7 > lengths[i] > 3:
                correct_lines += 1
    return correct_lines == number_of_verses


def is_seguidilla(lengths):
    """
    [7, 5, 7, 5]
    :param lengths:
    :return:
    """
    correct_lines = 0
    number_of_verses = len(lengths)
    if number_of_verses == 4:
        for i in (0, 2):
            if 9 > lengths[i] > 5:
                correct_lines += 1
        for i in (1, 3):
            if 7 > lengths[i] > 3:
                correct_lines += 1
    if correct_lines == number_of_verses:
        return True
    return False


def is_chamberga(lengths):
    """
    [7, 5, 7, 5, 3, 7, 3, 7, 3, 7]
    :param lengths:
    :return:
    """
    correct_lines = 0
    number_of_verses = len(lengths)
    if number_of_verses == 10:
        for i in (0, 2, 5, 7, 9):
            if 9 > lengths[i] > 5:
                correct_lines += 1
        for i in (1, 3):
            if 7 > lengths[i] > 4:
                correct_lines += 1
        for i in (4, 6, 8):
            if 6 > lengths[i] > 2:
                correct_lines += 1
    if correct_lines == number_of_verses:
        return True
    return False


def is_seguidilla_gitana(lengths):
    """
    [6, 6, 11, 6]
    :param lengths:
    :return:
    """
    correct_lines = 0
    number_of_verses = len(lengths)
    if number_of_verses == 4:
        for i in (0, 1, 3):
            if 8 > lengths[i] > 4:
                correct_lines += 1
        if 13 > lengths[2] > 9:
            correct_lines += 1
    if correct_lines == number_of_verses:
        return True
    return False


def is_cuarteto_lira_a(lengths):
    """
    [11, 7, 11, 7]
    :param lengths:
    :return:
    """
    correct_lines = 0
    number_of_verses = len(lengths)
    if number_of_verses == 4:
        for i in (0, 2):
            if 13 > lengths[i] > 8:
                correct_lines += 1
        for i in (1, 3):
            if 8 > lengths[i] > 5:
                correct_lines += 1
    if correct_lines == number_of_verses:
        return True
    return False


def is_cuarteto_lira_b(lengths):
    """
    [7, 11, 7, 11]
    :param lengths:
    :return:
    """
    correct_lines = 0
    number_of_verses = len(lengths)
    if number_of_verses == 4:
        for i in (0, 2):
            if 8 > lengths[i] > 5:
                correct_lines += 1
        for i in (1, 3):
            if 13 > lengths[i] > 8:
                correct_lines += 1
    if correct_lines == number_of_verses:
        return True
    return False


def is_estrofa_safica(lengths):
    """
    [11, 11, 11, 5]
    :param lengths:
    :return:
    """
    correct_lines = 0
    number_of_verses = len(lengths)
    if number_of_verses == 4:
        for i in (0, 1, 2):
            if 13 > lengths[i] > 8:
                correct_lines += 1
        if 7 > lengths[3] > 3:
            correct_lines += 1
    if correct_lines == number_of_verses:
        return True
    return False


def is_estrofa_safica_unamuno(lengths):
    """
    [11, 11, 7, 5]
    :param lengths:
    :return:
    """
    correct_lines = 0
    number_of_verses = len(lengths)
    if number_of_verses == 4:
        for i in (0, 1):
            if 13 > lengths[i] > 8:
                correct_lines += 1
        if 9 > lengths[2] > 5:
            correct_lines += 1
        if 7 > lengths[3] > 3:
            correct_lines += 1
    if correct_lines == number_of_verses:
        return True
    return False


def is_estrofa_francisco_de_la_torre(lengths):
    """
    [11, 11, 11, 7]
    :param lengths:
    :return:
    """
    correct_lines = 0
    number_of_verses = len(lengths)
    if number_of_verses == 4:
        for i in (0, 1, 2):
            if 13 > lengths[i] > 8:
                correct_lines += 1
        if 9 > lengths[3] > 5:
            correct_lines += 1
    if correct_lines == number_of_verses:
        return True
    return False


def is_endecha_real(lengths):
    """
    n*[7, 7, 7, 11]
    :param lengths:
    :return:
    """
    correct_lines = 0
    number_of_verses = len(lengths)
    if number_of_verses % 4 == 0 and number_of_verses > 7:
        for i in range(1, number_of_verses+1):
            if i % 4 != 0:
                if 9 > lengths[i-1] > 5:
                    correct_lines += 1
            if i % 4 == 0:
                if 13 > lengths[i-1] > 8:
                    correct_lines += 1
    if correct_lines == number_of_verses:
        return True
    return False


def is_lira(lengths):
    """
    [7, 11, 7, 7, 11]
    :param lengths:
    :return:
    """
    correct_lines = 0
    number_of_verses = len(lengths)
    if number_of_verses == 5:
        for i in (0, 2, 3):
            if 9 > lengths[i] > 5:
                correct_lines += 1
        for i in (1, 4):
            if 13 > lengths[i] > 8:
                correct_lines += 1
    if correct_lines == number_of_verses:
        return True
    return False


def is_estrofa_manriquena(lengths):
    """
    [8, 8, 4, 8, 8, 4]
    :param lengths:
    :return:
    """
    correct_lines = 0
    number_of_verses = len(lengths)
    if number_of_verses == 6:
        for i in (0, 1, 3, 4):
            if 10 > lengths[i] > 6:
                correct_lines += 1
        for i in (2, 5):
            if 6 > lengths[i] > 2:
                correct_lines += 1
    if correct_lines == number_of_verses:
        return True
    return False


def is_sexteto_lira_a(lengths):
    """
    [7, 11, 7, 11, 7, 11]
    :param lengths:
    :return:
    """
    correct_lines = 0
    number_of_verses = len(lengths)
    if number_of_verses == 6:
        for i in (0, 2, 4):
            if 10 > lengths[i] > 6:
                correct_lines += 1
        for i in (1, 3, 5):
            if 13 > lengths[i] > 9:
                correct_lines += 1
    if correct_lines == number_of_verses:
        return True
    return False


def is_sexteto_lira_b(lengths):
    """
    [11, 7, 11, 11, 7, 11]
    :param lengths:
    :return:
    """
    correct_lines = 0
    number_of_verses = len(lengths)
    if number_of_verses == 6:
        for i in (0, 2, 3, 5):
            if 13 > lengths[i] > 9:
                correct_lines += 1
        for i in (1, 4):
            if 8 > lengths[i] > 5:
                correct_lines += 1
    if correct_lines == number_of_verses:
        return True
    return False


def is_septeto_lira(lengths):
    """
    [7, 11, 7, 11, 7, 7, 11]
    :param lengths:
    :return:
    """
    correct_lines = 0
    number_of_verses = len(lengths)
    if number_of_verses == 7:
        for i in (0, 2, 4, 5):
            if 8 > lengths[i] > 5:
                correct_lines += 1
        for i in (1, 3, 6):
            if 13 > lengths[i] > 9:
                correct_lines += 1
    if correct_lines == number_of_verses:
        return True
    return False


def is_ovillejo(lengths):
    """
    [8, 4, 8, 4, 8, 4, 8, 8, 8, 8]
    :param lengths:
    :return:
    """
    correct_lines = 0
    number_of_verses = len(lengths)
    if number_of_verses == 10:
        for i in (0, 2, 4, 6, 7, 8, 9):
            if 10 > lengths[i] > 6:
                correct_lines += 1
        for i in (1, 3, 5):
            if 6 > lengths[i] > 2:
                correct_lines += 1
    if correct_lines == number_of_verses:
        return True
    return False


ASSONANT_RHYME = "assonant"
CONSONANT_RHYME = "consonant"

STRUCTURES = (
    (
        CONSONANT_RHYME,
        "seguidilla",
        r"(-a-a)|(abab)",
        is_seguidilla
    ), (
        ASSONANT_RHYME,
        "seguidilla",
        r"(-a-a)|(abab)",
        is_seguidilla
    ), (
        CONSONANT_RHYME,
        "seguidilla_compuesta",
        r"((-a-a)|(abab))((a-a)|(b-b)|(c-c))",
        is_seguidilla_compuesta
    ), (
        ASSONANT_RHYME,
        "seguidilla_compuesta",
        r"((-a-a)|(abab))((a-a)|(b-b)|(c-c))",
        is_seguidilla_compuesta
    ), (
        ASSONANT_RHYME,
        "chamberga",
        r"((-a-a)|(abab))([^-]{2}){3}",
        is_chamberga
    ), (
        ASSONANT_RHYME,
        "seguidilla_gitana",
        r"(-a-a)|(a-a-)",
        is_seguidilla_gitana
    ), (
        ASSONANT_RHYME,
        "endecha_real",
        r"(-a-a){2,}",
        is_endecha_real
    ), (
        CONSONANT_RHYME,
        "cuarteto_lira",
        r"(abab)|(abba)|(-a-a)",
        lambda lengths: all(
            x in most_common_lengths(lengths, n=3, number_of_verses=4) for x in
            [11, 7])
    ), (
        ASSONANT_RHYME,
        "cuarteto_lira",
        r"(abab)|(abba)|(-a-a)",
        lambda lengths: all(
            x in most_common_lengths(lengths, n=3, number_of_verses=4) for x in
            [11, 7])
    ), (
        CONSONANT_RHYME,
        "estrofa_sáfica",  # se puede encadenar?
        r"(----)|(a-a-)|(ab-b)|(abab)",
        is_estrofa_safica or is_estrofa_safica_unamuno
    ), (
        ASSONANT_RHYME,
        "estrofa_sáfica",  # se puede encadenar?
        r"(----)|(a-a-)|(ab-b)|(abab)",
        is_estrofa_safica
    ), (
        CONSONANT_RHYME,
        "estrofa_francisco_de_la_torre",
        r"(----)|(a-a-)",
        is_estrofa_francisco_de_la_torre
    ), (
        ASSONANT_RHYME,
        "francisco_de_la_torre",
        r"(----)|(a-a-)",
        is_estrofa_francisco_de_la_torre
    ), (
        CONSONANT_RHYME,
        "estrofa_manriqueña",
        r"abcabc",
        is_estrofa_manriquena
    ), (
        CONSONANT_RHYME,
        "sexteto_lira",
        r"(ababcc)|(aabccb)|(abcabc)",
        lambda lengths: all(
            x in most_common_lengths(lengths, number_of_verses=6) for x in
            [11, 7])
    ), (
        CONSONANT_RHYME,
        "septeto_lira",
        r"(ababbcc)",
        lambda lengths: all(
            x in most_common_lengths(lengths, number_of_verses=7) for x in
            [11, 7])
    ), (
        CONSONANT_RHYME,
        "ovillejo",
        r"aabbcccddc",
        is_ovillejo
    ), (
        CONSONANT_RHYME,
        "sonnet",
        r"(abba|abab|cddc|cdcd){2}((cd|ef){3}|(cde|efg){2}|[cde]{6})",
        lambda lengths: all(14 > length > 9 for length in lengths)
    ), (
        CONSONANT_RHYME,
        "couplet",
        r"aa",
        lambda lengths: all(20 > length > 1 for length in lengths)
    ), (
        CONSONANT_RHYME,
        "tercetillo",
        r"a.a",
        lambda lengths: all(11 > length > 1 for length in lengths)
    ), (
        CONSONANT_RHYME,
        "terceto",
        r"(aba)|(-aa)",
        lambda lengths: all(16 > length > 8 for length in lengths)
    ), (
        CONSONANT_RHYME,
        "sexteto",
        r"(aabccb)|(aababa)|(-aabba)",
        lambda lengths: all(16 > length > 9 for length in lengths)
    ), (
        CONSONANT_RHYME,
        "sexteto_rima",
        r"(ababcc)|(aacbbc)",
        lambda lengths: statistics.median(lengths) == 11
    ), (
        CONSONANT_RHYME,
        "sextilla",
        r"(aabaab)|(abcabc)|(ababab)|(abbccb)|(aababa)",
        lambda lengths: all(11 > length > 4 for length in lengths)
    ), (
        CONSONANT_RHYME,
        "terceto_monorrimo",
        r"aaa",
        lambda lengths: all(16 > length > 8 for length in lengths)
    ), (
        CONSONANT_RHYME,
        "redondilla",
        r"abba",
        lambda lengths: all(10 > length > 4 for length in lengths)
    ), (
        ASSONANT_RHYME,
        "redondilla",
        r"abba",
        lambda lengths: all(10 > length > 4 for length in lengths)
    ), (
        CONSONANT_RHYME,
        "aleluya",
        r"((.)\2){3,}",
        lambda lengths: all(11 > length > 4 for length in lengths)
    ), (
        CONSONANT_RHYME,
        "cuarteto",
        r"abba",
        lambda lengths: all(16 > length > 8 for length in lengths)
    ), (
        CONSONANT_RHYME,
        "serventesio",
        r"abab",
        lambda lengths: all(16 > length > 8 for length in lengths)
    ), (
        CONSONANT_RHYME,
        "cuaderna_vía",
        r"aaaa",
        lambda lengths: statistics.median(lengths) == 14
    ), (
        CONSONANT_RHYME,
        "cuarteta",
        r"abab",
        lambda lengths: all(10 > length > 4 for length in lengths)
    ), (
        CONSONANT_RHYME,
        "octava_real",
        r"(abababcc)",
        lambda lengths: statistics.median(lengths) == 11
    ), (
        CONSONANT_RHYME,
        "copla_arte_mayor",
        r"(abbaacca)|(ababbccb)|(abbaacac)",
        lambda lengths: all(16 > length > 8 for length in lengths)
    ), (
        CONSONANT_RHYME,
        "copla_arte_menor",
        r"(abbaacca)|(ababbccb)|(abbaacac)",
        lambda lengths: statistics.median(lengths) == 8 or (
            all(x in most_common_lengths(lengths) for x in [8, 4]))
    ), (
        CONSONANT_RHYME,
        "copla_castellana",
        r"(abbacddc)|(ababcdcd)|(abbacdcd)|(ababcddc)|(abbaacca)",
        lambda lengths: statistics.median(lengths) == 8
    ),  (
        CONSONANT_RHYME,
        "copla_mixta",
        r"abbacca",
        lambda lengths: all(11 > length > 3 for length in lengths)
    ), (
        CONSONANT_RHYME,
        "octava",
        r".{8}",
        lambda lengths: all(16 > length > 8 for length in lengths)
    ), (
        CONSONANT_RHYME,
        "octavilla",
        r"(abbecdde)|(ababbccb)",
        lambda lengths: all(11 > length > 4 for length in lengths)
    ), (
        ASSONANT_RHYME,
        "octavilla",
        r"(abbecdde)|(ababbccb)",
        lambda lengths: all(11 > length > 4 for length in lengths)
    ), (
        CONSONANT_RHYME,
        "espinela",
        r"abbaaccddc",
        lambda lengths: statistics.median(lengths) == 8
    ), (
        CONSONANT_RHYME,
        "copla_real",
        r"""((ababa)|(abaab)|(abbab)|(aabab)|(aabba))
        ((ababa)|(abaab)|(abbab)|(aabab)|(aabba)
        (cdcdc)|(cdccd)|(cddcd)|(ccdcd)|(ccddc))""",
        # tiene versos quebrados, cambiar regla de lengths
        lambda lengths: statistics.median(lengths) == 8
    ), (
        CONSONANT_RHYME,
        "lira",
        r"ababb",
        is_lira
    ), (
        CONSONANT_RHYME,
        "quinteto",
        r"(ababa|abaab|abbab|aabab|aabba)",
        lambda lengths: all(14 > length > 9 for length in lengths)
    ), (
        CONSONANT_RHYME,
        "quintilla",
        r"(ababa|abaab|abbab|aabab|aabba)",
        lambda lengths: all(11 > length > 3 for length in lengths)
    ), (
        ASSONANT_RHYME,
        "couplet",
        r"aa",
        lambda lengths: all(20 > length > 1 for length in lengths)
    ), (
        ASSONANT_RHYME,
        "silva_arromanzada",
        r"(-a)+",
        lambda lengths: all(x in most_common_lengths(lengths) for x in [11, 7])
    ), (
        ASSONANT_RHYME,
        "cantar",
        r"-a-a",
        lambda lengths: all(11 > length > 4 for length in lengths)
    ), (
        ASSONANT_RHYME,
        "romance",
        r"((.b)+)|(([^a]a)+)",
        lambda lengths: statistics.median(lengths) == 8
    ), (
        ASSONANT_RHYME,
        "romance_arte_mayor",
        r"((.b)+)|((.a)+)",
        lambda lengths: 11 <= statistics.median(lengths) <= 14
    ), (
        ASSONANT_RHYME,
        "haiku",
        r".*",
        lambda lengths: re.compile(r"(575)+").match("".join(
            [str(length) for length in lengths]
        ))
    ), (
        ASSONANT_RHYME,
        "soleá",
        r"(a-a)",
        lambda lengths: statistics.median(lengths) == 8
    ), (
        CONSONANT_RHYME,
        "decima_antigua",
        r"(abbaacccaa)",
        lambda lengths: statistics.median(lengths) == 8
    ), (
        CONSONANT_RHYME,
        "septeto",
        r".{7}",
        lambda lengths: all(16 > length > 8 for length in lengths)
    ), (
        CONSONANT_RHYME,
        "septilla",
        r".{7}",
        lambda lengths: all(11 > length > 4 for length in lengths)
    ), (
        CONSONANT_RHYME,
        "novena",
        r".{9}",
        lambda _: True
    )
)

STRUCTURES_LENGTH = {
    "sonnet": 14 * [11],
    "haiku": [5, 7, 5],
    "lira": [7, 11, 7, 7, 11]
}
