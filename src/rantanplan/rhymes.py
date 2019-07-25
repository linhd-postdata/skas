import re
import statistics
import string

from spacy_affixes.utils import strip_accents


def get_stressed_endings(scansion):
    """Return a list of word endings, from the stressed position,
    from a scansion list of tokens"""
    endings = []
    for line in scansion:
        words = [word for word in line["tokens"] if "symbol" not in word]
        syllables_count = sum(len(word["word"]) for word in words)
        last_word = words[-1]
        last_word_ending = last_word["word"][last_word["stress_position"]:]
        ending = [syllable["syllable"] for syllable in last_word_ending]
        endings.append((ending, syllables_count, last_word["stress_position"]))
    return endings


CONSONANTS = r"bcdfghjklmnñpqrstvwxyz"
UNSTRESSED_VOWELS = r"aeiou"
STRESSED_VOWELS = r"áéíóúäëïöü"
WEAK_VOWELS = r"iuïü"
STRONG_VOWELS = r"aeoáéó"
WEAK_VOWELS_RE = re.compile(fr'[{WEAK_VOWELS}]([{STRONG_VOWELS}])',
                            re.U | re.I)
VOWELS = fr"{UNSTRESSED_VOWELS}{STRESSED_VOWELS}"
STRESSED_VOWELS_RE = re.compile(fr'[{STRESSED_VOWELS}]', re.U | re.I)
CONSONANTS_RE = re.compile(fr'[{CONSONANTS}]+', re.U | re.I)
INITIAL_CONSONANTS_RE = re.compile(fr'^[{CONSONANTS}]+', re.U | re.I)
DIPHTHONG_H_RE = re.compile(fr'([{VOWELS}])h([{VOWELS}])', re.U | re.I)
DIPHTHONG_Y_RE = re.compile(fr'([{VOWELS}])h?y([^{VOWELS}])', re.U | re.I)
STRUCTURES = (
    (
        "consonant",
        "sonnet",
        r"(abba|abab|cddc|cdcd){2}((cd|ef){3}|(cde|efg){2})",
        lambda syllables: all(13 > syl > 10 for syl in syllables)
    ),
    ("consonant", "couplet", r"aa", lambda x: True),
    (
        "assonant",
        "romance",
        r"((.b)+)|((.a)+)",
        lambda syllables: statistics.median(syllables) == 8
    ),
    (
        "assonant",
        "haiku",
        r".*",
        lambda syllables: re.compile(r"(575)+").match("".join(
            [str(syl)for syl in syllables]
        ))
    ),
    ("assonant", "couplet", r"aa", lambda _: True),
)


def get_rhymes(stressed_endings, assonance=False, relaxation=False,
               offset=None, free_verse_symbol="-"):
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
    lines i and i + offset. The symbol for free verse can be set
    using free_verse_symbol (defaults to '-')"""
    codes = {}
    code_numbers = []
    unique = set()
    # Clean consonants as needed and assign numeric codes
    for stressed_ending, _, stressed_position in stressed_endings:
        stressed_ending_upper = stressed_ending[stressed_position].upper()
        stressed_ending[stressed_position] = stressed_ending_upper
        if relaxation:
            ending = "".join(WEAK_VOWELS_RE.sub(r"\1", syll, count=1)
                             for syll in stressed_ending)
        else:
            ending = "".join(stressed_ending)
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
    code2endings = {v: k for k, v in codes.items()}
    # Adjust for free verses and assign letter codes
    letters = {}
    rhymes = []
    endings = []
    last_found = {}
    for index, rhyme in enumerate(code_numbers):
        if rhyme in unique:
            rhyme_letter = -1  # free verse
            endings.append("")
        else:
            if rhyme not in letters:
                letters[rhyme] = len(letters)
            rhyme_letter = letters[rhyme]
            # Reassign free verses if an offset is set
            if (rhyme in last_found
                    and offset is not None
                    and index - last_found[rhyme] > offset):
                rhymes[last_found[rhyme]] = -1  # free verse
                endings[last_found[rhyme]] = ''
            last_found[rhyme] = index
            endings.append(code2endings[rhyme])
        rhymes.append(rhyme_letter)
    # Reorder letters
    rhyme_letters = []
    letters = {}
    stresses = []
    for rhyme in rhymes:
        if rhyme < 0:  # free verse
            rhyme_letter = free_verse_symbol
        else:
            if rhyme not in letters:
                letters[rhyme] = len(letters)
            rhyme_letter = string.ascii_letters[letters[rhyme]]
        rhyme_letters.append(rhyme_letter)
    # Extract stress
    stresses = []
    for index, ending in enumerate(endings):
        if not ending:
            stresses.append(0)
        ending_lower = ending.lower()
        if ending_lower != ending:
            positions = [pos - len(ending)
                         for pos, char in enumerate(ending)
                         if char.isupper()]
            stresses.append(positions[0])  # only return first stress detected
            endings[index] = ending_lower
    return rhyme_letters, endings, stresses


def search_structure_index(rhyme, syllables_count, structure_key):
    for index, (key, _, structure, func) in enumerate(STRUCTURES):
        if (key == structure_key
                and re.compile(structure).match(rhyme)
                and func(syllables_count)):
            return index


def get_analysis(scansion, offset=4):
    """Analyze the syllables of a text to propose a possible set of
    rhyme structure, rhyme name, rhyme endings, and rhyme pattern"""
    stressed_endings = get_stressed_endings(scansion)
    best_ranking = len(STRUCTURES)
    best_structure = None
    # Prefer consonance to assonance
    for assonance in (False, True):
        rhyme_type = "assonant" if assonance else "consonant"
        # Prefer relaxation to stricness
        for relaxation in (True, False):
            rhymes, endings, endings_stress = get_rhymes(
                stressed_endings, assonance, relaxation, offset
            )
            rhyme = "".join(rhymes)
            syllable_count = [count for _, count, _ in stressed_endings]
            ranking = search_structure_index(rhyme, syllable_count, rhyme_type)
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
        return best_structure["name"], best_structure
