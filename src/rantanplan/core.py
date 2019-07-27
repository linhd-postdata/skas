#!/usr/bin/python
# Based on previous work done by Rafael C. Carrasco, José A. Mañas (Communications of the ACM 30(7), 1987)
# and Javier Sober
# https://github.com/postdataproject/skas-archived/blob/devel/skas/phonmet/syll/grapheme2syllable.py
#
# Presyllabification and syllabification rules are taken from Antonio Ríos Mestre's
# 'El Diccionario Electrónico Fonético del Español'
# https://www.raco.cat/index.php/Elies/article/view/194843
# http://elies.rediris.es/elies4/Fon2.htm
# http://elies.rediris.es/elies4/Fon8.htm
import re

from spacy.tokens import Doc

from .alternative_syllabification import ALTERNATIVE_SYLLABIFICATION
from .pipeline import load_pipeline
from .rhymes import analyze_rhyme

"""
Syllabification
"""
accents_re = re.compile("[áéíóú]", re.I | re.U)
paroxytone_re = re.compile("([aeiou]|n|[aeiou]s)$", re.I | re.U)  # checks if a str ends in unaccented vowel/N/S

letter_clusters_re = re.compile(r"""
    # 1: weak vowels diphthong with h
    ([iuü]h[iuü])|
    # 2: open vowels
    ([aáeéíoóú]h[iuü])|
    # 3: closed vowels
    ([iuü]h[aáeéíoóú])|
    # 4: liquid and mute consonants (adds hyphen)
    ([a-záéíóúñ](?:(?:[bcdfghjklmnñpqsvxyz][hlr])|(?:[bcdfghjklmnñpqrstvxyz][hr]))[aáeéiíoóuúü])|
    # 5: any char followed by liquid and mute consonant, exceptions for 'r+l' and 't+l'
    ((?:(?:[bcdfghjklmnñpqsvxyz][hlr])|(?:[bcdfghjklmnñpqrstvxyz][hr]))[aáeéiíoóuúü])|
    # 6: non-liquid consonant (adds hyphen)
    ([a-záéíóúñ][bcdfghjklmnñpqrstvxyz][aáeéiíoóuúüï])|
    # 7: vowel group (adds hyphen)
    ([aáeéíoóú][aáeéíoóú])|
    # 8: umlaut 'u' diphthongs
    (ü[eií])|
    # 9: Explicit hiatus with umlaut vowels, first part
    ([aeiou][äëïöü])|
    #10: Explicit hiatus with umlaut vowels, second part
    ([äëïöü][a-z])|
    #12: any char
    ([a-záéíóúñ])
""", re.I | re.U | re.VERBOSE)  # re.VERBOSE is needed to be able to catch the regex group

"""
Metrical Analysis
"""
STRONG_VOWELS = set("aeoáéóÁÉÓAEO")
WEAK_VOWELS = set("iuüíúIÍUÜÚ")
LIAISON_FIRST_PART = set("aeiouáéíóúAEIOUÁÉÍÓÚy")
LIAISON_SECOND_PART = set("aeiouáéíóúAEIOUÁÉÍÓÚhy")
STRESSED_UNACCENTED_MONOSYLLABLES = {"yo", "vio", "dio", "fe", "sol", "ti", "un"}
UNSTRESSED_UNACCENTED_MONOSYLLABLES = {'de', 'el', 'la', 'las', 'le', 'les', 'lo', 'los',
                                       'mas', 'me', 'mi', 'nos', 'os', 'que', 'se', 'si',
                                       'su', 'tan', 'te', 'tu'}


"""
Regular expressions and rules for syllabification exceptions

"""

# words starting with ABROG-
ABROG_RE = re.compile("^(ab)(rog[au].*)", re.I | re.U)

# words starting with OBREP-
OBREP_RE = re.compile("^(ob)(rep.*)", re.I | re.U)

# words starting with prefixes SIN-/DES- followed by consonant "destituir", "sinhueso"
PREFIXES_WITH_CONSONANT_RE = (re.compile("^(des|sin)([bcdfgjklmhnñpqrstvxyz].*)", re.I | re.U))

# words with prefix EN- followed by consonant: "entrampar", "abencerraje"
PREFIX_EN_WITH_CONSONANT_RE = (re.compile("(.*?en)([bcdfgjklmhnñpqrstvxyz].*)", re.I | re.U))

# group rh + u[aeiou] dipthongs : "marhuenda"
PREFIX_RNH_DIPTHONG_RE = (re.compile("(.*?r)(hu[aeioáéíó].*)", re.I | re.U))


"""
Metrical Analysis functions
"""


def have_prosodic_liaison(first_syllable, second_syllable):
    """
    Checkfor prosodic liaison between two syllables
    :param first_syllable: dic with key syllable (str) and is_stressed (bool) representing the first syllable
    :param second_syllable: dic with key syllable (str) and is_stressed (bool) representing the second syllable
    :return: True if there is prosodic liaison and False otherwise
    :rtype: bool
    """
    return (first_syllable['syllable'][-1] in LIAISON_FIRST_PART
            and second_syllable['syllable'][0] in LIAISON_SECOND_PART)


"""
Syllabifier functions
"""


def apply_exception_rules(word):
    # 'Abrogar' and derivatives
    if ABROG_RE.match(word):
        match = ABROG_RE.search(word)
        if match is not None:
            word = "-".join(match.groups())
    # 'Obrepticio' and derivatives
    if OBREP_RE.match(word):
        match = OBREP_RE.search(word)
        if match is not None:
            word = "-".join(match.groups())
    # Prefix 'en' followed by consonant
    if PREFIX_EN_WITH_CONSONANT_RE.match(word):
        match = PREFIX_EN_WITH_CONSONANT_RE.search(word)
        if match is not None:
            word = "-".join(match.groups())
    # Prefix 'des'/'sin' followed by consonant
    if PREFIXES_WITH_CONSONANT_RE.match(word):
        match = PREFIXES_WITH_CONSONANT_RE.search(word)
        if match is not None:
            word = "-".join(match.groups())
    # Group rh followed by u + dipthong
    if PREFIX_RNH_DIPTHONG_RE.match(word):
        match = PREFIX_RNH_DIPTHONG_RE.search(word)
        if match is not None:
            word = "-".join(match.groups())
    return word


def syllabify(word):
    """
    Syllabifies a word.
    :param word: The word to be syllabified.
    :return: list of syllables and exceptions where appropriate.
    :rtype: list
    """
    output = ""
    original_word = word
    word = apply_exception_rules(word)
    while len(word) > 0:
        output += word[0]
        # Returns first matching pattern.
        m = letter_clusters_re.search(word)
        if m is not None:
            # Adds hyphen to syllables if regex pattern is not 5, 8, 11
            output += "-" if m.lastindex not in set([5, 8, 11]) else ""
        word = word[1:]
    # Remove empty elements created during syllabification
    output = list(filter(bool, output.split("-")))
    return output, ALTERNATIVE_SYLLABIFICATION.get(original_word, (None, ()))[1]


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


def is_paroxytone(syllable_list):
    """
    Given a list of str representing syllables from a single word, check is it is paroxytonic (llana) or not
    :param syllable_list: List of syllables as str
    :return: True if paroxytone, False if not
    :rtype: bool
    """
    if not get_orthographic_accent("".join(syllable_list)):
        return paroxytone_re.search(syllable_list[len(syllable_list) - 1]) is not None
    return False


def spacy_tag_to_dict(tag):
    """
    Creater a dict from spacy pos tags
    :param tag: Extended spacy pos tag ("Definite=Ind|Gender=Masc|Number=Sing|PronType=Art")
    :return: A dictionary in the form of "{'Definite': 'Ind', 'Gender': 'Masc', 'Number': 'Sing', 'PronType': 'Art'}"
    :rtype: dict
    """
    if tag and '=' in tag:
        return dict([t.split('=') for t in tag.split('|')])
    else:
        return {}


def get_word_stress(word, pos, tag):
    """
    Gets a list of syllables from a word and creates a list with syllabified word and stressed syllable index
    :param word: List of str representing syllables
    :param pos: PoS tag from spacy ("DET")
    :param tag: Extended PoS tag info from spacy ("Definite=Ind|Gender=Masc|Number=Sing|PronType=Art")
    :return: Dict with [original syllab word, stressed syllab. word, negative index position of stressed syllable or 0 if not stressed]
    :rtype: dict
    """
    syllable_list, _ = syllabify(word)
    if len(syllable_list) == 1:
        if ((syllable_list[0].lower() not in UNSTRESSED_UNACCENTED_MONOSYLLABLES)
                and ((syllable_list[0].lower() in STRESSED_UNACCENTED_MONOSYLLABLES)
                     or (pos not in ("DET", "PRON", "ADP"))
                     or (pos == "PRON" and tag.get("Case") == "Nom")
                     or (pos == "DET" and tag.get("Definite") == "Ind"))):
            stressed_position = -1
        else:
            stressed_position = 0  # unstressed monosyllable
    else:
        tilde = get_orthographic_accent(syllable_list)
        # If an orthographic accent exists, that syllable negative index is saved.
        if tilde is not None:
            stressed_position = -(len(syllable_list) - tilde)
        # Else if the word is paroxytone (llana) we save the penultimate syllable.
        elif is_paroxytone(syllable_list):
            stressed_position = -2
        # If the word does not meet the above criteria that means that it's an oxytone word (aguda).
        else:
            stressed_position = -1
    out_syllable_list = []
    for index, syllable in enumerate(syllable_list):
        out_syllable_list.append(
            {"syllable": syllable, "is_stressed": len(syllable_list) - index == -stressed_position})
        if index < 1:
            continue
        # Sinaeresis
        first_syllable = syllable_list[index - 1]
        second_syllable = syllable
        if first_syllable and second_syllable and (
                (first_syllable[-1] in STRONG_VOWELS and second_syllable[0] in STRONG_VOWELS)
                or (first_syllable[-1] in WEAK_VOWELS and second_syllable[0] in STRONG_VOWELS)
                or (first_syllable[-1] in STRONG_VOWELS and second_syllable[0] in WEAK_VOWELS)):
            out_syllable_list[index-1].update({'has_sinaeresis': True})
    return {
        'word': out_syllable_list, "stress_position": stressed_position,
    }


def get_last_syllable(token_list):
    """
    Gets last syllable from a word in a dictionary
    :param token_list: list of dictionary tokens
    :return: Last syllable
    """
    if len(token_list) > 0:
        for token in token_list[::-1]:
            if 'word' in token:
                return token['word'][-1]


def get_syllables(word_list):
    """
    Gets a list of syllables from a word and creates a list with syllabified word and stressed syllabe index
    :param word_list: List of spacy objects representing a word or sentence
    :return: List with [original syllab. word, stressed syllab. word, negative index position of stressed syllable]
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
            stressed_word = get_word_stress(word.text, pos, tags)
            first_syllable = get_last_syllable(syllabified_words)
            second_syllable = stressed_word['word'][0]
            # Synalepha
            if first_syllable and second_syllable and have_prosodic_liaison(first_syllable, second_syllable):
                first_syllable.update({'has_synalepha': True})
            syllabified_words.append(stressed_word)
        else:
            syllabified_words.append({"symbol": word.text})
    return syllabified_words


def get_scansion(text, rhyme_analysis=False):
    """
    Generates a list of dictionaries for each line
    :param text: Full text to be analyzed
    :param rhyme_analysis: Specify if rhyme analysis is to be performed
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
    for token in tokens:
        if token.pos_ == "SPACE" and '\n' in token.orth_ and len(seen_tokens) > 0:
            lines.append({"tokens": get_syllables(seen_tokens)})
            seen_tokens = []
        else:
            seen_tokens.append(token)
    if len(seen_tokens) > 0:
        lines.append({"tokens": get_syllables(seen_tokens)})
    if rhyme_analysis:
        for rhyme in analyze_rhyme(lines):
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
    return lines
