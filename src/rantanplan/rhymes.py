# -*- coding: utf-8 -*-
import re
import string
from collections import Counter

from spacy_affixes.utils import strip_accents

from rantanplan.structures import ASSONANT_RHYME
from rantanplan.structures import CONSONANT_RHYME
from rantanplan.structures import STRUCTURES
from rantanplan.utils import argcount
from rantanplan.utils import generate_exceeded_offset_indices

CONSONANTS = r"bcdfghjklmnñpqrstvwxyz"
UNSTRESSED_VOWELS = r"aeiou"
STRESSED_VOWELS = r"áéíóúäëïöü"
TILDED_VOWELS = r"áéíóú"
WEAK_VOWELS = r"iuïü"
STRONG_VOWELS = r"aeoáéó"
WEAK_STRONG_VOWELS_RE = re.compile(fr'[{WEAK_VOWELS}](h?[{STRONG_VOWELS}])',
                                   re.U | re.I)
STRONG_WEAK_VOWELS_RE = re.compile(fr'([{STRONG_VOWELS}]h?)[{WEAK_VOWELS}]',
                                   re.U | re.I)
WEAK_WEAK_VOWELS_RE = re.compile(fr'[{WEAK_VOWELS}](h?[{WEAK_VOWELS}])',
                                 re.U | re.I)
STRONG_STRONG_VOWELS_RE = re.compile(fr'[{STRONG_VOWELS}](h?[{STRONG_VOWELS}])',
                                     re.U | re.I)
VOWELS = fr"{UNSTRESSED_VOWELS}{STRESSED_VOWELS}"
STRESSED_VOWELS_RE = re.compile(fr'[{STRESSED_VOWELS}]', re.U | re.I)
TILDED_VOWELS_RE = re.compile(fr'[{TILDED_VOWELS}]', re.U | re.I)
CONSONANTS_RE = re.compile(fr'[{CONSONANTS}]+', re.U | re.I)
INITIAL_CONSONANTS_RE = re.compile(fr'^[{CONSONANTS}]+', re.U | re.I)
DIPHTHONG_H_RE = re.compile(fr'([{VOWELS}])h([{VOWELS}])', re.U | re.I)
DIPHTHONG_Y_RE = re.compile(fr'([{VOWELS}])h?y([^{VOWELS}])', re.U | re.I)
GROUP_GQ_RE = re.compile(r'([qg])u([ei])', re.U | re.I)
HOMOPHONES = [
    ("v", "b"), ("ll", "y"),
    ("ze", "ce"), ("zi", "ci"),
    ("qui", "ki"), ("que", "ke"),
    ("ge", "je"), ("gi", "ji"),
]


def get_ending_with_liaison(phonological_group, liaison):
    """Get position of the tilded vowel from a phonological group with a liaison
    and uses that index to get the rhyming syllable
    """
    has_tilded_vowel = TILDED_VOWELS_RE.search(
        phonological_group["syllable"])
    if has_tilded_vowel:
        liaison_index = has_tilded_vowel.start()
    else:
        liaison_index = phonological_group[f"{liaison}_index"][-1] + 1
    syllable = phonological_group["syllable"][liaison_index:]
    return syllable


def get_stressed_endings(lines):
    """Return a list of word endings starting at the stressed position,
    from a scansion lines list of tokens as input"""
    endings = []
    for line in lines:
        syllables = []
        for phonological_group in line["phonological_groups"]:
            # Break groups on last synalepha index position if present
            if "synalepha_index" in phonological_group:
                syllable = get_ending_with_liaison(
                    phonological_group, "synalepha")
            elif "sinaeresis_index" in phonological_group:
                syllable = get_ending_with_liaison(
                    phonological_group, "sinaeresis")
            else:
                syllable = phonological_group["syllable"]
            syllables.append(syllable)
        syllables_count = len(syllables)
        syllables_stresses = [syllable["is_stressed"]
                              for syllable in line["phonological_groups"]]
        inverted_stresses = syllables_stresses[::-1]
        last_stress_index = (
            len(inverted_stresses) - inverted_stresses.index(True) - 1
        )
        ending = syllables[last_stress_index:]
        endings.append(
            (ending, syllables_count, last_stress_index - syllables_count)
        )
    return endings


def get_clean_codes(stressed_endings, assonance=False, relaxation=False):
    """Clean syllables from stressed_endings depending on the rhyme kind,
    assonance or consonant, and some relaxation of diphthongs for rhyming
    purposes. Stress is also marked by upper casing the corresponding
    syllable. The codes for the endings and the rhymes in numerical form
    are returned."""
    codes = {}
    code_numbers = []
    # Clean consonants as needed and assign numeric codes
    for stressed_ending, _, stressed_position in stressed_endings:
        syllable = stressed_ending[stressed_position]
        # If there is a tilde, only upper case that vowel
        match = TILDED_VOWELS_RE.search(syllable)
        if match:
            span = match.span()
            syllable = (syllable[:span[0]] + match.group().upper()
                        + syllable[span[1]:])
        # Otherwise, only the final if there is a diphthong
        else:
            syllable = syllable.upper()
        stressed_ending[stressed_position] = syllable
        # TODO: Other forms of relaxation should be tried iteratively, such as
        # changing `i` for `e`, etc.
        if relaxation:
            relaxed_endings = []
            for syllable in stressed_ending:
                relaxed_syllable = WEAK_STRONG_VOWELS_RE.sub(
                    r"\1", syllable, count=1)
                relaxed_syllable = STRONG_WEAK_VOWELS_RE.sub(
                    r"\1", relaxed_syllable, count=1)
                relaxed_syllable = WEAK_WEAK_VOWELS_RE.sub(
                    r"\1", relaxed_syllable, count=1)
                # Homophones
                for find, change in HOMOPHONES:
                    relaxed_syllable = relaxed_syllable.replace(find, change)
                    relaxed_syllable = relaxed_syllable.replace(
                        find.upper(), change.upper()
                    )
                relaxed_endings.append(relaxed_syllable)
            ending = "".join(relaxed_endings)
        else:
            ending = "".join(stressed_ending)
        ending = GROUP_GQ_RE.sub(r"\1\2", ending)
        ending = DIPHTHONG_Y_RE.sub(r"\1i\2", ending)
        if assonance:
            ending = CONSONANTS_RE.sub(r"", ending)
        else:
            # Consonance
            ending = DIPHTHONG_H_RE.sub(r"\1\2", ending)
            ending = INITIAL_CONSONANTS_RE.sub(r"", ending, count=1)
        ending = strip_accents(ending)
        if ending not in codes:
            codes[ending] = len(codes)
        code_numbers.append(codes[ending])
    # Invert codes to endings
    codes2endings = {v: k for k, v in codes.items()}
    return codes2endings, code_numbers


def apply_offset(codes, ending_codes, offset=4):
    """Control how many lines of distance should a matching rhyme occur at.
    An offset can be set to an arbitrary number, effectively allowing rhymes
    that only occur between lines i and i + offset, and assigning a new rhyme
    code when the offset is exceeded, even if the ending appeared before."""
    code_numbers = ending_codes.copy()
    offset_indices = generate_exceeded_offset_indices(code_numbers, offset)
    for offset_index in offset_indices:
        max_code = max(code_numbers) + 1
        code_numbers = (
            code_numbers[:offset_index]
            + [max_code if code == code_numbers[offset_index] else code
               for code in code_numbers[offset_index:]]
        )
        codes[max_code] = codes[ending_codes[offset_index]]
    return codes, code_numbers


def assign_letter_codes(codes, code_numbers, unrhymed_verses):
    """Adjust for unrhymed verses and assign consecutive codes.
    """
    rhyme_codes = {}
    rhymes = []
    endings = []
    for rhyme in code_numbers:
        if rhyme in unrhymed_verses:
            endings.append('')  # do not track unrhymed verse endings
            rhymes.append(-1)  # unrhymed verse
        else:
            if rhyme not in rhyme_codes:
                rhyme_codes[rhyme] = len(rhyme_codes)
            endings.append(codes[rhyme])
            rhymes.append(rhyme_codes[rhyme])
    return rhymes, endings


def rhyme_codes_to_letters(rhymes, unrhymed_verse_symbol="-"):
    """Reorder rhyme letters so first rhyme is always an 'a'."""
    sorted_rhymes = []
    letters = {}
    for rhyme in rhymes:
        if rhyme < 0:  # unrhymed verse
            rhyme_letter = unrhymed_verse_symbol
        else:
            if rhyme not in letters:
                letters[rhyme] = len(letters)
            rhyme_letter = string.ascii_letters[letters[rhyme]]
        sorted_rhymes.append(rhyme_letter)
    return sorted_rhymes


def split_stress(endings):
    """Extract stress from endings and return the split result"""
    stresses = []
    unstressed_endings = []
    for index, ending in enumerate(endings):
        unstressed_endings.append(ending)
        if not ending:
            stresses.append(0)
        ending_lower = ending.lower()
        if ending_lower != ending:
            positions = [pos - len(ending)
                         for pos, char in enumerate(ending)
                         if char.isupper()]
            stresses.append(positions[0])  # only return first stress detected
            unstressed_endings[index] = ending_lower
    return stresses, unstressed_endings


def get_rhymes(stressed_endings, assonance=False, relaxation=False,
               offset=None, unrhymed_verse_symbol=None):
    """From a list of syllables from the last stressed syllable of the ending
    word of each line (stressed_endings), return a tuple with two lists:
    - rhyme pattern of each line (e.g., a, b, b, a)
    - rhyme ending of each line (e.g., ado, ón, ado, ón)
    The rhyme checking method can be assonant (assonance=True) or
    consonant (default). Moreover, some diphthongs relaxing rules can be
    applied (relaxation=False) so the weak vowels are removed when checking
    the ending syllables.
    By default, all verses are checked, that means that a poem might match
    lines 1 and 100 if the ending is the same. To control how many lines
    should a matching rhyme occur, an offset can be set to an arbitrary
    number, effectively allowing rhymes that only occur between
    lines i and i + offset. The symbol for unrhymed verse can be set
    using unrhymed_verse_symbol (defaults to '-')"""
    if unrhymed_verse_symbol is None:
        unrhymed_verse_symbol = "-"
    # Get a numerical representation of rhymes using numbers
    codes, ending_codes = get_clean_codes(
        stressed_endings, assonance, relaxation
    )
    # Apply offset to codes and ending_codes
    if offset is not None:
        codes, ending_codes = apply_offset(codes, ending_codes, offset)
    # Get the indices of unrhymed verses
    unrhymed_verses = argcount(ending_codes, count=1)
    # Get the actual rhymes and endings adjusting for unrhymed verses
    rhyme_codes, endings = assign_letter_codes(
        codes, ending_codes, unrhymed_verses
    )
    # Assign and reorder rhyme letters so first rhyme is always an 'a'
    rhymes = rhyme_codes_to_letters(rhyme_codes, unrhymed_verse_symbol)
    # Extract stress from endings
    stresses, unstressed_endings = split_stress(endings)
    return rhymes, unstressed_endings, stresses


def search_structure(rhyme, length_ranges, structure_key, structures=None):
    """Search in stanza structures for a structure that matches assonance or
    consonance, a rhyme pattern (regex or callable), and a condition on the
    lengths of syllables of lines. For the first matching structure, its index
    in STRUCTURES will be returned. An alternative STRUCTURES list can be passed
    in structures."""
    if structures is None:
        structures = STRUCTURES
    indices = []
    for index, (key, _, structure, func) in enumerate(structures):
        if callable(structure):
            structure_check = structure(rhyme)
        else:  # it's a regex
            structure_re = re.compile(structure, re.VERBOSE)
            structure_check = structure_re.fullmatch(rhyme)
        if (key == structure_key
                and structure_check
                and func(length_ranges)):
            indices.append(index)
    return indices


def analyze_rhyme(lines, offset=4, always_return_rhyme=False):
    """Analyze the syllables of a text to propose a possible set of
    rhyme structure, rhyme name, rhyme endings, and rhyme pattern"""
    stressed_endings = get_stressed_endings(lines)
    best_ranking = len(STRUCTURES)
    best_structure = None
    analyses = []
    # Prefer consonance to assonance
    for assonance in (False, True):
        rhyme_type = ASSONANT_RHYME if assonance else CONSONANT_RHYME
        # Prefer relaxation to strictness
        for relaxation in (True, False):
            rhymes, endings, endings_stress = get_rhymes(
                stressed_endings, assonance, relaxation, offset
            )
            rhyme = "".join(rhymes)
            length_ranges = [
                range(line["rhythm"]["length_range"]["min_length"],
                      line["rhythm"]["length_range"]["max_length"] + 1)
                for line in lines]
            analysis = {
                "rhyme": rhymes,
                "endings": endings,
                "endings_stress": endings_stress,
                "rhyme_type": rhyme_type,
                "rhyme_relaxation": relaxation
            }
            candidates = search_structure(rhyme, length_ranges, rhyme_type)
            if len(candidates):
                ranking, *_ = candidates
            else:
                ranking = None
            if ranking is not None and ranking < best_ranking:
                best_ranking = ranking
                best_structure = {
                    "name": STRUCTURES[best_ranking][1],
                    "rank": best_ranking,
                    "rhyme": rhymes,
                    "endings": endings,
                    "endings_stress": endings_stress,
                    "rhyme_type": rhyme_type,
                    "rhyme_relaxation": relaxation
                }
            else:
                analyses.append(analysis)
    if best_structure is not None:
        return best_structure
    elif always_return_rhyme:
        best_candidate = get_best_rhyme_candidate(analyses)
        return best_candidate


def get_best_rhyme_candidate(candidates):
    """From a list of candidates, return the one with the most rhymed verses,
    with priority:
        1 - consonant rhyme and relaxing rules
        2 - consonant rhyme and no relaxing rules
        3 - assonant rhyme and no relaxing rules
        4 - assonant rhyme and no relaxing rules
    :param candidates: List of analyzed_lines
    :type candidates: list
    :return: Best rhyme candidate
    :rtype: dict
    """
    n_rhymes = 0
    candidate_index = 0
    for index, candidate in enumerate(candidates):
        n_rhymes_candidate = len(candidates[0]["rhyme"]) - Counter(
            candidate["rhyme"]).get('-', 0)
        if n_rhymes_candidate > n_rhymes:
            n_rhymes = n_rhymes_candidate
            candidate_index = index
    return candidates[candidate_index]
