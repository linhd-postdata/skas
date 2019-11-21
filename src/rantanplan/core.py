#!/usr/bin/python
# Based on previous work done by Rafael C. Carrasco, José A. Mañas
# (Communications of the ACM 30(7), 1987) and Javier Sober
# https://github.com/postdataproject/skas-archived/blob/devel/skas/phonmet/syll/grapheme2syllable.py
#
# Presyllabification and syllabification rules are taken from
# Antonio Ríos Mestre's 'El Diccionario Electrónico Fonético del Español'
# https://www.raco.cat/index.php/Elies/article/view/194843
# http://elies.rediris.es/elies4/Fon2.htm
# http://elies.rediris.es/elies4/Fon8.htm
import re
from itertools import product

from spacy.tokens import Doc

from .alternative_syllabification import ALTERNATIVE_SYLLABIFICATION
from .alternative_syllabification import SYLLABIFICATOR_FOREIGN_WORDS_DICT
from .pipeline import load_pipeline
from .rhymes import STRUCTURES_LENGTH
from .rhymes import analyze_rhyme

"""
Syllabification
"""
accents_re = re.compile("[áéíóú]", re.I | re.U)
paroxytone_re = re.compile("([aeiou]|n|[aeiou]s)$",
                           # checks if a str ends in unaccented vowel/N/S
                           re.I | re.U)

"""
Regular expressions for spanish syllabification.
For the 'tl' cluster we have decided to join the two letters
because is the most common syllabification and the same that
Perkins (http://sadowsky.cl/perkins.html), DIRAE (https://dirae.es/),
and Educalingo (https://educalingo.com/es/dic-es) use.
"""
letter_clusters_re = re.compile(r"""
    # 1: weak vowels diphthong with h
    ([iuü]h[iuü])|
    # 2: open vowels
    ([aáeéíoóú]h[iuü])|
    # 3: closed vowels
    ([iuü]h[aáeéíoóú])|
    # 4: liquid and mute consonants (adds hyphen)
    ([a-záéíóúñ](?:(?:[bcdfghjklmnñpqstvy][hlr])|
    (?:[bcdfghjklmnñpqrstvy][hr])|
    (?:[bcdfghjklmnñpqrstvyz][h]))[aáeéiíoóuúü])|
    # 5: any char followed by liquid and mute consonant,
    # exceptions for 'r+l' and 't+l'
    ((?:(?:[bcdfghjklmnñpqstvy][hlr])|
    (?:[bcdfghjklmnñpqrstvy][hr])|
    (?:[bcdfghjklmnñpqrstvyz][h]))[aáeéiíoóuúü])|
    # 6: non-liquid consonant (adds hyphen)
    ([a-záéíóúñ][bcdfghjklmnñpqrstvxyz][aáeéiíoóuúüï])|
    # 7: vowel group (adds hyphen)
    ([aáeéíoóú][aáeéíoóú])|
    # 8: umlaut 'u' diphthongs
    (ü[iíaeo])|
    # 9: Explicit hiatus with umlaut vowels, first part
    ([aeiou][äëïöü])|
    #10: Explicit hiatus with umlaut vowels, second part
    ([üäëïö][a-z])|
    #11: any char
    ([a-záéíóúñ])""", re.I | re.U | re.VERBOSE)  # VERBOSE to catch the group

"""
Rhythmical Analysis
"""
SPACE = "SPACE"
STRONG_VOWELS = set("aeoáéóÁÉÓAEO")
WEAK_VOWELS = set("iuüíúIÍUÜÚ")
LIAISON_FIRST_PART = set("aeiouáéíóúAEIOUÁÉÍÓÚyY")
LIAISON_SECOND_PART = set("aeiouáéíóúAEIOUÁÉÍÓÚhyYH")
STRESSED_UNACCENTED_MONOSYLLABLES = {"yo", "vio", "dio", "fe", "sol", "ti",
                                     "un"}
UNSTRESSED_UNACCENTED_MONOSYLLABLES = {'de', 'el', 'la', 'las', 'le', 'les',
                                       'lo', 'los',
                                       'mas', 'me', 'mi', 'nos', 'os', 'que',
                                       'se', 'si',
                                       'su', 'tan', 'te', 'tu', "tus", "oh"}
UNSTRESSED_FORMS = {"que", "cual", "quien", "donde", "cuando", "cuanto",
                    "como"}

POSSESSIVE_PRON = {"mío", "mía", "míos", "mías", "tuyo", "tuya", "tuyos",
                   "tuyas", "suyo", "suya", "suyos", "suyas"}

POSSESSIVE_PRON_UNSTRESSED = {"nuestro", "nuestra", "nuestros", "nuestras",
                              "vuestro", "vuestra", "vuestros", "vuestras"}

"""
Regular expressions and rules for syllabification exceptions
"""

# Words starting with prefixes SIN-/DES- followed by consonant "destituir"
PREFIX_DES_WITH_CONSONANT_RE = (
    re.compile("^(des)([bcdfgjklmhnñpqrstvxyz].*)", re.I | re.U))

# Words starting with prefixes SIN-/DES- followed by consonant "sinhueso"
PREFIX_SIN_WITH_CONSONANT_RE = (
    re.compile("^(sin)([bcdfgjklmhnñpqrstvxyz].*)", re.I | re.U))

# Group consonant+[hlr] with exceptions for ll
CONSONANT_GROUP = (re.compile("(.*[hmnqsw])([hlr][aeiouáéíóú].*)", re.I | re.U))
CONSONANT_GROUP_EXCEPTION_LL = (
    re.compile("(.*[hlmnqsw])([hr][aeiouáéíóú].*)", re.I | re.U))
CONSONANT_GROUP_EXCEPTION_DL = (
    re.compile("(.*[d])([l][aeiouáéíóú].*)", re.I | re.U))

# Group vowel+ w + vowel
W_VOWEL_GROUP = (re.compile("(.*[aeiouáéíóú])(w[aeiouáéíóú].*)", re.I | re.U))

# Post-syllabification exceptions for consonant clusters and diphthongs
# Explicitit hiatus on first vowel
HIATUS_FIRST_VOWEL_RE = (re.compile(
    "(?:(.*-)|^)([äëïö]|[^g]ü)([aeiouúáéíó].*)",
    re.I | re.U | re.VERBOSE))

# Consonant cluster. Example: 'cneorácea'
CONSONANT_CLUSTER_RE = (re.compile(
    "(?:(.*-)|^)([mpgc])-([bcdfghjklmñnpqrstvwxyz][aeioáéíó].*)",
    re.I | re.U | re.VERBOSE))

# Lowering diphthong. Example: 'ahijador'
LOWERING_DIPHTHONGS_WITH_H = (
    re.compile(
        """((?:.*-|^)(?:qu|[bcdfghjklmñnpqrstvwxyz]+)?)
        ([aeo])-(h[iu](?![aeoiuíúáéó]).*)""",
        re.I | re.U | re.VERBOSE))

# Lowering diphthong. Example: 'buhitiho'
RAISING_DIPHTHONGS_WITH_H = (
    re.compile(
        """((?:.*-|^)(?:qu|[bcdfghjklmñnpqrstvwxyz]+)?)
        ([iu])-(h[aeiouáéó](?![aeoáéiuíú]).*)""",
        re.I | re.U | re.VERBOSE))

"""
Rhythmical Analysis functions
"""


def have_prosodic_liaison(first_syllable, second_syllable):
    """
    Checkfor prosodic liaison between two syllables
    :param first_syllable: dic with key syllable (str) and is_stressed (bool)
                           representing the first syllable
    :param second_syllable: dic with key syllable (str) and is_stressed (bool)
                            representing the second syllable
    :return: True if there is prosodic liaison and False otherwise
    :rtype: bool
    """
    if second_syllable['syllable'][0].lower() == 'y' and (
            len(second_syllable['syllable']) > 1) and (
            second_syllable['syllable'][1].lower() in set('aeiouáéíúó')):
        return False
    else:
        return (first_syllable['syllable'][-1] in LIAISON_FIRST_PART
                and second_syllable['syllable'][0] in LIAISON_SECOND_PART)


def get_syllables_word_end(words):
    """
    Get a list of syllables from a list of words extracting word boundaries
    :param words: List of dictonaries of syllables for each word in a line
    :return: List of dictionaries of syllables with an extra is_word_end key
    """
    syllables = []
    for word in words:
        if "symbol" in word:
            continue
        for i, syllable in enumerate(word["word"]):
            if i == len(word["word"]) - 1:
                syllable["is_word_end"] = True
            syllables.append(syllable)
    return syllables


def get_phonological_groups(word_syllables, liaison_type="synalepha",
                            breakage_func=None, liaison_positions=None):
    """
    Get a list of dictionaries for each phonological group on a line
    and joins the syllables to create phonological groups (pronounced together)
    according to a type of liaison, either synaloepha or sinaeresis
    :param word_syllables: List of dictionaries for each word of the line
    :param liaison_type: Which liaison is going to be performed synalepha or
                         sinaeresis
    :param breakage_func: Function to decide when not to break a liaison that is
    specified in liaison_positions
    :param liaison_positions: Positions of the liaisons
    :return: A list of conjoined syllables
    """
    syllables = word_syllables[:]
    liaison_property = f"has_{liaison_type}"
    if liaison_positions is None:
        liaison_positions = [int(syllable.get(liaison_property, 0))
                             for syllable in syllables]
    skip_next = False
    while sum(liaison_positions) > 0:
        liaison_index = []
        reduced_syllables = []
        for idx, syllable in enumerate(syllables):
            if skip_next:
                skip_next = False
                continue
            breakage = False
            if idx < len(syllables) - 1:
                next_syllable = syllables[idx + 1]
                breakage = (
                        breakage_func is not None
                        and breakage_func(liaison_type, syllable, next_syllable)
                )
            if liaison_positions[idx] and not breakage:
                boundary_index = syllable.get(f'{liaison_type}_index', [])
                boundary_index.append(len(syllable.get('syllable')) - 1)
                liaison = {
                    'syllable': (syllable["syllable"]
                                 + next_syllable["syllable"]),
                    'is_stressed': (syllable["is_stressed"]
                                    or next_syllable["is_stressed"]),
                    f'{liaison_type}_index': boundary_index,
                }
                for prop in (liaison_property, "is_word_end"):
                    has_prop = next_syllable.get(prop, None)
                    if has_prop is not None:
                        liaison[prop] = has_prop
                reduced_syllables.append(liaison)
                liaison_index.append(liaison_positions[idx + 1])
                skip_next = True
            else:
                reduced_syllables.append(syllable)
                liaison_index.append(0)
        liaison_positions = liaison_index
        syllables = reduced_syllables
    return clean_phonological_groups(
        syllables, liaison_positions, liaison_property
    )


def clean_phonological_groups(groups, liaison_positions, liaison_property):
    """
    Clean phonological groups so their liaison property is consistently set
    according to the the liaison positions
    :param groups: Phonological groups to be cleaned
    :param liaison_positions: Positions of the liaisons
    :param liaison_property: The liaison type (synaeresis or synalepha)
    :return:
    """
    clean_groups = []
    for idx, group in enumerate(groups):
        if liaison_property in group:
            clean_groups.append({
                **group, liaison_property: bool(liaison_positions[idx])
            })
        else:
            clean_groups.append(group)
    return clean_groups


def get_rhythmical_pattern(phonological_groups, rhythm_format="pattern"):
    """
    Gets a rhythm pattern for a poem in either "pattern": "-++-+-+-"
    "binary": "01101010" or "indexed": [1,2,4,6] format
    :param phonological_groups: a dictionary with the syllables of the line
    :param rhythm_format: The output format for the rhythm
    :return: Dictionary with with rhythm and phonologic groups
    """
    stresses = get_stresses(phonological_groups)
    stress = format_stress(stresses, rhythm_format)
    return {
        "stress": stress,
        "type": rhythm_format,
        "length": len(stresses)
    }


def get_stresses(phonological_groups):
    """
    Gets a list of stress marks (True for stressed, False for unstressed) from a
    list of phonological groups applying rules depending on the ending stress.
    :param phonological_groups: a dictionary with the phonological groups
    (syllables) of the line
    :return: List of boolean values indicating whether a group is
    stressed (True) or not (False)
    """
    stresses = [group["is_stressed"] for group in phonological_groups]
    last_stress = -(stresses[::-1].index(True) + 1)
    # Oxytone (Aguda)
    if last_stress == -1:
        stresses.append(False)
    # Paroxytone (Esdrújula) or Proparoxytone (Sobreesdrújula)
    elif last_stress <= -3:
        stresses.pop()
    return stresses


def format_stress(stresses, rhythm_format="pattern", indexed_separator="-"):
    """
    Converts a list of boolean elements into a string that matches the chosen
    rhythm format:
                "indexed": 2,5,8
                "pattern": -++--+-+-
                "binary": 01101001
    :param stresses: List of boolean elements representing stressed syllables
    :param rhythm_format: Format to be used: indexed, pattern, or binary
    :param indexed_separator: String to use as a separator for indexed pattern
    :return: String with the stress pattern
    """
    separator = ""
    if rhythm_format == 'indexed':
        stresses = [
            str(index + 1) for index, stress in enumerate(stresses) if stress
        ]
        separator = indexed_separator
    elif rhythm_format == 'binary':
        stresses = map(lambda stress: str(int(stress)), stresses)
    else:  # rhythm_format == 'pattern':
        stresses = map(lambda stress: "+" if stress else "-", stresses)
    return separator.join(stresses)


"""
Syllabifier functions
"""


def apply_exception_rules(word):
    """
    Applies presyllabification rules to a word,
    based on Antonio Ríos Mestre's work
    :param word: A string to be checked for exceptions
    :return: A string with the presyllabified word
    """
    # Vowel + w + vowel group
    if W_VOWEL_GROUP.match(word):
        match = W_VOWEL_GROUP.search(word)
        if match is not None:
            word = "-".join(match.groups())
    # Consonant groups with exceptions for LL and DL
    if CONSONANT_GROUP.match(word):
        match = CONSONANT_GROUP.search(word)
        if match is not None:
            word = "-".join(match.groups())
    if CONSONANT_GROUP_EXCEPTION_LL.match(word):
        match = CONSONANT_GROUP_EXCEPTION_LL.search(word)
        if match is not None:
            word = "-".join(match.groups())
    if CONSONANT_GROUP_EXCEPTION_DL.match(word):
        match = CONSONANT_GROUP_EXCEPTION_DL.search(word)
        if match is not None:
            word = "-".join(match.groups())
    # Prefix 'sin' followed by consonant
    if PREFIX_SIN_WITH_CONSONANT_RE.match(word):
        match = PREFIX_SIN_WITH_CONSONANT_RE.search(word)
        if match is not None:
            word = "-".join(match.groups())
    # Prefix 'des' followed by consonant
    if PREFIX_DES_WITH_CONSONANT_RE.match(word):
        match = PREFIX_DES_WITH_CONSONANT_RE.search(word)
        if match is not None:
            word = "-".join(match.groups())
    return word


def apply_exception_rules_post(word):
    """
    Applies presyllabification rules to a word,
    based on Antonio Ríos Mestre's work
    :param word: A string to be checked for exceptions
    :return: A string with the presyllabified word with hyphens
    """
    # We make one pass for every match found so we can perform
    # several substitutions
    matches = HIATUS_FIRST_VOWEL_RE.findall(word)
    if matches:
        for _ in matches[0]:
            word = re.sub(HIATUS_FIRST_VOWEL_RE, r'\1\2-\3', word)
    regexes = (CONSONANT_CLUSTER_RE, LOWERING_DIPHTHONGS_WITH_H,
               RAISING_DIPHTHONGS_WITH_H)
    for regex in regexes:
        matches = regex.findall(word)
        if matches:
            for _ in matches[0]:
                word = re.sub(regex, r'\1\2\3', word)
    return word


def syllabify(word, alternative_syllabification=False):
    """
    Syllabifies a word.
    :param word: The word to be syllabified.
    :param alternative_syllabification: Wether or not the alternative
    syllabification is used
    :return: list of syllables and exceptions where appropriate.
    :rtype: list
    """
    output = ""
    original_word = word
    # Checks if word exists on the foreign words dictionary
    if word in SYLLABIFICATOR_FOREIGN_WORDS_DICT:
        output = SYLLABIFICATOR_FOREIGN_WORDS_DICT[word]
    else:
        word = apply_exception_rules(word)
        while len(word) > 0:
            output += word[0]
            # Returns first matching pattern.
            m = letter_clusters_re.search(word)
            if m is not None:
                # Adds hyphen to syllables if regex pattern is not 5, 8, 11
                output += "-" if m.lastindex not in {5, 8, 11} else ""
            word = word[1:]
        output = apply_exception_rules_post(output)
    # Remove empty elements created during syllabification
    output = list(filter(bool, output.split("-")))
    if (alternative_syllabification
            and original_word.lower() in ALTERNATIVE_SYLLABIFICATION):
        return ALTERNATIVE_SYLLABIFICATION[original_word.lower()][1][0]
    else:
        return (output,
                ALTERNATIVE_SYLLABIFICATION.get(original_word, (None, ()))[1])


def get_orthographic_accent(syllable_list):
    """
    Given a list of str representing syllables,
    return position in the list of a syllable bearing
    orthographic stress (with the acute accent mark in Spanish)
    :param syllable_list: list of syllables as str or unicode each
    :return: Position or None if no orthographic stress
    :rtype: int
    """
    word = "|".join(syllable_list)
    match = accents_re.search(word)
    position = None
    if match is not None:
        last_index = match.span()[0]
        position = word[:last_index].count("|")
    return position


def is_paroxytone(syllables):
    """
    Given a list of str representing syllables from a single word,
    check if it is paroxytonic (llana) or not
    :param syllables: List of syllables as str
    :return: True if paroxytone, False if not
    :rtype: bool
    """
    if not get_orthographic_accent("".join(syllables)):
        return paroxytone_re.search(syllables[len(syllables) - 1]) is not None
    return False


def spacy_tag_to_dict(tag):
    """
    Creater a dict from spacy pos tags
    :param tag: Extended spacy pos tag
    ("Definite=Ind|Gender=Masc|Number=Sing|PronType=Art")
    :return: A dictionary in the form of
    "{'Definite': 'Ind', 'Gender': 'Masc', 'Number': 'Sing', 'PronType': 'Art'}"
    :rtype: dict
    """
    if tag and '=' in tag:
        return dict([t.split('=') for t in tag.split('|')])
    else:
        return {}


def get_word_stress(word, pos, tag, alternative_syllabification=False):
    """
    Gets a list of syllables from a word and creates a list with syllabified
    word and stressed syllable index
    :param word: List of str representing syllables
    :param alternative_syllabification: Wether or not the alternative
    syllabification is used
    :param pos: PoS tag from spacy ("DET")
    :param tag: Extended PoS tag info from spacy
    ("Definite=Ind|Gender=Masc|Number=Sing|PronType=Art")
    :return: Dict with [original syllab word, stressed syllabified word,
    negative index position of stressed syllable or 0
    if not stressed]
    :rtype: dict
    """
    syllable_list, _ = syllabify(word, alternative_syllabification)
    word_lower = "".join(word).lower()
    if len(syllable_list) == 1:
        first_monosyllable = syllable_list[0].lower()
        if ((first_monosyllable not in UNSTRESSED_UNACCENTED_MONOSYLLABLES)
                and (first_monosyllable in STRESSED_UNACCENTED_MONOSYLLABLES
                     or pos not in ("SCONJ", "CCONJ", "DET", "PRON", "ADP")
                     or (pos == "PRON" and tag.get("Case") == "Nom")
                     or (pos == "DET" and tag.get("Definite") in (
                         "Dem", "Ind"))
                     or pos in ("PROPN", "NUM", "NOUN", "VERB", "AUX", "ADV")
                     or (pos == "ADJ" and tag.get("Poss", None) != "Yes")
                     or (pos == "PRON"
                         and tag.get("PronType", None) in ("Prs", "Ind"))
                     or (pos == "DET" and tag.get("PronType", None) == "Ind")
                     or (pos in ("ADJ", "DET"
                                        and tag.get("Poss", None) == "Yes"))
                     or (pos in ("PRON", "DET")
                         and tag.get("PronType", None) in (
                                 "Exc", "Int", "Dem"))
                     or "".join(word).lower() in POSSESSIVE_PRON)):
            stressed_position = -1
        else:
            stressed_position = 0  # unstressed monosyllable
    elif (pos in ("INTJ", "PROPN", "NUM", "NOUN", "VERB", "AUX", "ADV")
          or pos == "ADJ" and word_lower not in POSSESSIVE_PRON_UNSTRESSED
          or (pos == "PRON" and tag.get("PronType", None) in ("Prs", "Ind"))
          or (pos == "DET" and tag.get("PronType", None) in ("Dem", "Ind"))
          or (pos == "DET" and tag.get("Definite", None) == "Ind")
          or (pos == "PRON" and tag.get("Poss", None) == "Yes")
          or (pos in ("PRON", "DET")
              and tag.get("PronType", None) in ("Exc", "Int", "Dem"))
          or (word_lower in POSSESSIVE_PRON)):
        tilde = get_orthographic_accent(syllable_list)
        # If an orthographic accent exists, the syllable negative index is saved
        if tilde is not None:
            stressed_position = -(len(syllable_list) - tilde)
        # Elif the word is paroxytone (llana) we save the penultimate syllable.
        elif is_paroxytone(syllable_list):
            stressed_position = -2
        # If the word does not meet the above criteria that means that it's an
        # oxytone word (aguda).
        else:
            stressed_position = -1
    else:
        stressed_position = 0  # unstressed
    out_syllable_list = []
    for index, syllable in enumerate(syllable_list):
        out_syllable_list.append(
            {"syllable": syllable,
             "is_stressed": len(syllable_list) - index == -stressed_position})
        if index < 1:
            continue
        # Sinaeresis
        first_syllable = syllable_list[index - 1]
        second_syllable = syllable
        if first_syllable and second_syllable and (
                (first_syllable[-1] in STRONG_VOWELS
                 and second_syllable[0] in STRONG_VOWELS)
                or (first_syllable[-1] in WEAK_VOWELS
                    and second_syllable[0] in STRONG_VOWELS)
                or (first_syllable[-1] in STRONG_VOWELS
                    and second_syllable[0] in WEAK_VOWELS)):
            out_syllable_list[index - 1].update({'has_sinaeresis': True})
    return {
        'word': out_syllable_list, "stress_position": stressed_position,
    }


def get_last_syllable(token_list):
    """
    Gets last syllable from a word in a dictionary
    :param token_list: list of dictionaries with line tokens
    :return: Last syllable
    """
    if len(token_list) > 0:
        for token in token_list[::-1]:
            if 'word' in token:
                return token['word'][-1]


def get_words(word_list, alternative_syllabification=False):
    """
    Gets a list of syllables from a word and creates a list with syllabified
    word and stressed syllabe index
    :param word_list: List of spacy objects representing a word or sentence
    :param alternative_syllabification: Wether or not the alternative
    syllabification is used
    :return: List with [original syllab. word, stressed syllab. word, negative
    index position of stressed syllable]
    :rtype: list
    """
    syllabified_words = []
    for word in word_list:
        if word.is_alpha:
            if '__' in word.tag_:
                pos, tag = word.tag_.split('__')
            else:
                pos = word.pos_ or ""
                tag = word.tag_ or ""
            tags = spacy_tag_to_dict(tag)
            stressed_word = get_word_stress(word.text, pos, tags,
                                            alternative_syllabification)
            first_syllable = get_last_syllable(syllabified_words)
            second_syllable = stressed_word['word'][0]
            # Synalepha
            if first_syllable and second_syllable and have_prosodic_liaison(
                    first_syllable, second_syllable):
                first_syllable.update({'has_synalepha': True})
            syllabified_words.append(stressed_word)
        else:
            syllabified_words.append({"symbol": word.text})
    return syllabified_words


def get_scansion(text, rhyme_analysis=False, rhythm_format="pattern",
                 rhythmical_lengths=None):
    """
    Generates a list of dictionaries for each line
    :param text: Full text to be analyzed
    :param rhyme_analysis: Specify if rhyme analysis is to be performed
    :param rhythm_format: output format for rhythm analysis
    :param rhythmical_lengths: List with explicit rhythmical lengths per line
    that the analysed lines has to meet
    :return: list of dictionaries per line
    :rtype: list
    """
    if isinstance(text, Doc):
        tokens = text
    else:
        nlp = load_pipeline()
        tokens = nlp(text)
    seen_tokens = []
    lines = []
    raw_tokens = []
    # Handle multi-line sentences and create the line with words
    for token in tokens:
        if (token.pos_ == SPACE
                and '\n' in token.orth_
                and len(seen_tokens) > 0):
            lines.append({"tokens": get_words(seen_tokens, True)})
            raw_tokens.append(seen_tokens)
            seen_tokens = []
        else:
            seen_tokens.append(token)
    if len(seen_tokens) > 0:
        lines.append({"tokens": get_words(seen_tokens, True)})
        raw_tokens.append(seen_tokens)
    # Extract phonological groups and rhythm per line
    for line in lines:
        syllables = get_syllables_word_end(line["tokens"])
        phonological_groups = get_phonological_groups(
            get_phonological_groups(syllables, liaison_type="sinaeresis")
        )
        line.update({
            "phonological_groups": phonological_groups,
            "rhythm": get_rhythmical_pattern(phonological_groups, rhythm_format)
        })
    if rhyme_analysis:
        analyzed_lines = analyze_rhyme(lines)
        if analyzed_lines is not None:
            for rhyme in [analyzed_lines]:
                for index, line in enumerate(lines):
                    line["structure"] = rhyme["name"]
                    line["rhyme"] = rhyme["rhyme"][index]
                    line["ending"] = rhyme["endings"][index]
                    line["ending_stress"] = rhyme["endings_stress"][index]
                    if line["ending_stress"] == 0:
                        line["rhyme_type"] = ""
                        line["rhyme_relaxation"] = None
                    else:
                        line["rhyme_type"] = rhyme["rhyme_type"]
                        line["rhyme_relaxation"] = rhyme["rhyme_relaxation"]
    for idx, line in enumerate(lines):
        if rhythmical_lengths is not None:
            structure_length = rhythmical_lengths
        else:
            line_structure = line.get("structure", None)
            structure_length = STRUCTURES_LENGTH.get(line_structure, None)
        if structure_length is not None:
            if line["rhythm"]["length"] < structure_length[idx]:
                candidates = generate_phonological_groups(raw_tokens[idx])
                for candidate in candidates:
                    rhythm = get_rhythmical_pattern(
                        candidate, rhythm_format)
                    if rhythm["length"] == structure_length[idx]:
                        line.update({
                            "phonological_groups": candidate,
                            "rhythm": rhythm,
                        })
                        break
    return lines


def break_on_h(liaison_type, syllable_left, syllable_right):
    return (
            liaison_type == "synalepha"
            and syllable_right["syllable"][0].lower() == "h"
    )


def generate_phonological_groups(tokens):
    """
    Generates phonological groups from a list of tokens
    :param tokens: list of spaCy tokens
    :return: Generator with a list of phonological groups
    """
    for alternative_syllabification in (True, False):
        words = get_words(tokens, alternative_syllabification)
        syllables = get_syllables_word_end(words)
        for liaison in (
                ("synalepha",),
                ("sinaeresis",),
                ("sinaeresis", "synalepha"),
                ("synalepha", "sinaeresis"),
        ):
            for ignore_synalepha_h in (break_on_h, None):
                for liaison_positions_1 in generate_liaison_positions(
                        syllables, liaison[0]
                ):
                    groups = get_phonological_groups(
                        syllables[:],
                        liaison_type=liaison[0],
                        liaison_positions=liaison_positions_1,
                        breakage_func=ignore_synalepha_h,
                    )
                    if len(liaison) == 1:
                        yield groups
                    else:
                        for liaison_positions_2 in generate_liaison_positions(
                            syllables, liaison[1]
                        ):
                            yield get_phonological_groups(
                                groups,
                                liaison_type=liaison[1],
                                liaison_positions=liaison_positions_2,
                                breakage_func=ignore_synalepha_h,
                            )


def generate_liaison_positions(syllables, liaison):
    """
    Generates all possible combinations for the liaisons on a list of syllables
    :param syllables: List of syllables with
    :param liaison: Type of liaison combination to be generated
    :return: Generator with a list of possible combinations
    """
    positions = [int(syllable.get(f"has_{liaison}", 0))
                 for syllable in syllables]
    # Combinations start by applying all possible liaisons: [1, 1, ...]
    combinations = list(product([1, 0], repeat=sum(positions)))
    liaison_indices = [
        index for index, position in enumerate(positions) if position
    ]
    for combination in combinations:
        liaison_positions = [0] * len(positions)
        for index, liaison_index in enumerate(liaison_indices):
            liaison_positions[liaison_index] = combination[index]
        yield liaison_positions
