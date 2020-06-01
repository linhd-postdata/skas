# -*- coding: utf-8 -*-
import re
import string

from spacy_affixes.utils import strip_accents

from rantanplan.structures import ASSONANT_RHYME
from rantanplan.structures import CONSONANT_RHYME
from rantanplan.structures import STRUCTURES

CONSONANTS = r"bcdfghjklmnñpqrstvwxyz"
UNSTRESSED_VOWELS = r"aeiou"
STRESSED_VOWELS = r"áéíóúäëïöü"
TILDED_VOWELS = r"áéíóú"
WEAK_VOWELS = r"iuïü"
STRONG_VOWELS = r"aeoáéó"
WEAK_VOWELS_RE = re.compile(fr'[{WEAK_VOWELS}]([{STRONG_VOWELS}])',
                            re.U | re.I)
VOWELS = fr"{UNSTRESSED_VOWELS}{STRESSED_VOWELS}"
STRESSED_VOWELS_RE = re.compile(fr'[{STRESSED_VOWELS}]', re.U | re.I)
TILDED_VOWELS_RE = re.compile(fr'[{TILDED_VOWELS}]', re.U | re.I)
CONSONANTS_RE = re.compile(fr'[{CONSONANTS}]+', re.U | re.I)
INITIAL_CONSONANTS_RE = re.compile(fr'^[{CONSONANTS}]+', re.U | re.I)
DIPHTHONG_H_RE = re.compile(fr'([{VOWELS}])h([{VOWELS}])', re.U | re.I)
DIPHTHONG_Y_RE = re.compile(fr'([{VOWELS}])h?y([^{VOWELS}])', re.U | re.I)
GROUP_GQ_RE = re.compile(fr'([qg])u([ei])', re.U | re.I)
HOMOPHONES = [
    ("v", "b"), ("ll", "y"),
    ("ze", "ce"), ("zi", "ci"),
    ("qui", "ki"), ("que", "ke"),
    ("ge", "je"), ("gi", "ji"),
]


def get_stressed_endings(lines):
    """Return a list of word endings starting at the stressed position,
    from a scansion lines list of tokens as input"""
    endings = []
    for line in lines:
        syllables = []
        for phonological_group in line["phonological_groups"]:
            # Break groups on last synalepha index position if present
            if "synalepha_index" in phonological_group:
                synalepha_index = phonological_group["synalepha_index"][-1] + 1
                syllable = phonological_group["syllable"][synalepha_index:]
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
    syllable. The codes for the endings, the rhymes in numerical form, and
    a set with endings of possible unrhymed verses are returned."""
    codes = {}
    code_numbers = []
    unique = set()
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
                relaxed_syllable = WEAK_VOWELS_RE.sub(r"\1", syllable, count=1)
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
            unique.add(codes[ending])
        else:
            unique.discard(codes[ending])
        code_numbers.append(codes[ending])
    # Invert codes to endings
    codes2endings = {v: k for k, v in codes.items()}
    return codes2endings, code_numbers, unique


def assign_letter_codes(codes, code_numbers, unrhymed_verses, offset=None):
    """Adjust for unrhymed verses and assign letter codes.
    By default, all verses are checked, that means that a poem might match
    lines 1 and 100 if the ending is the same. To control how many lines
    should a matching rhyme occur in, an offset can be set to an arbitrary
    number, effectively allowing rhymes that only occur between
    lines i and i + offset."""
    letters = {}
    rhymes = []
    endings = []
    last_found = {}
    for index, rhyme in enumerate(code_numbers):
        if rhyme in unrhymed_verses:
            rhyme_letter = -1  # unrhymed verse
            endings.append('')  # do not track unrhymed verse endings
            rhymes.append(rhyme_letter)
        else:
            if rhyme not in letters:
                letters[rhyme] = len(letters)
            rhyme_letter = letters[rhyme]
            # Reassign unrhymed verses if an offset is set
            if (rhyme in last_found
                    and offset is not None
                    and index - last_found[rhyme] > offset):
                rhymes[last_found[rhyme]] = -1  # unrhymed verse
                endings[last_found[rhyme]] = ''  # unrhymed verse ending
                endings.append('')
                rhymes.append(-1)
            else:
                endings.append(codes[rhyme])
                rhymes.append(rhyme_letter)
            last_found[rhyme] = index
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
    consonant (default). Moreover, some dipthongs relaxing rules can be
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
    # Get a numerical representation of rhymes using numbers and
    # identifying unrhymed verses
    codes, ending_codes, unrhymed_verses = get_clean_codes(
        stressed_endings, assonance, relaxation
    )
    # Get the actual rhymes and endings adjusting for unrhymed verses
    rhyme_codes, endings = assign_letter_codes(
        codes, ending_codes, unrhymed_verses, offset
    )
    # Assign and reorder rhyme letters so first rhyme is always an 'a'
    rhymes = rhyme_codes_to_letters(rhyme_codes, unrhymed_verse_symbol)
    # Extract stress from endings
    stresses, unstressed_endings = split_stress(endings)
    return rhymes, unstressed_endings, stresses


def search_structure(rhyme, rhythmical_lengths, structure_key, structures=None):
    """Search in stanza structures for a structure that matches assonance or
    consonance, a rhyme pattern, and a condition on the lengths of sylalbles
    of lines. For the first matching structure, its index in STRUCTURES will
    be returned. An alternative STRUCTURES list can ba passed in structures."""
    if structures is None:
        structures = STRUCTURES
    for index, (key, _, structure, func) in enumerate(structures):
        if (key == structure_key
                and re.compile(structure, re.VERBOSE).fullmatch(rhyme)
                and func(rhythmical_lengths)):
            return index


def analyze_rhyme(lines, offset=4):
    """Analyze the syllables of a text to propose a possible set of
    rhyme structure, rhyme name, rhyme endings, and rhyme pattern"""
    stressed_endings = get_stressed_endings(lines)
    best_ranking = len(STRUCTURES)
    best_structure = None
    # Prefer consonance to assonance
    for assonance in (False, True):
        rhyme_type = ASSONANT_RHYME if assonance else CONSONANT_RHYME
        # Prefer relaxation to strictness
        for relaxation in (True, False):
            rhymes, endings, endings_stress = get_rhymes(
                stressed_endings, assonance, relaxation, offset
            )
            rhyme = "".join(rhymes)
            rhythmical_lengths = [line["rhythm"]["length"] for line in lines]
            ranking = search_structure(rhyme, rhythmical_lengths, rhyme_type)
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
    if best_structure is not None:
        return best_structure
