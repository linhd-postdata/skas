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
import copy
import re

from spacy.tokens import Doc

from .alternative_syllabification import ALTERNATIVE_SYLLABIFICATION
from .alternative_syllabification import SYLLABIFICATOR_FOREIGN_WORDS_DICT
from .pipeline import load_pipeline
from .rhymes import analyze_rhyme

"""
Syllabification
"""
accents_re = re.compile("[áéíóú]", re.I | re.U)
paroxytone_re = re.compile("([aeiou]|n|[aeiou]s)$", re.I | re.U)  # checks if a str ends in unaccented vowel/N/S


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
    ([a-záéíóúñ](?:(?:[bcdfghjklmnñpqstvy][hlr])|(?:[bcdfghjklmnñpqrstvy][hr])|(?:[bcdfghjklmnñpqrstvyz][h]))[aáeéiíoóuúü])|
    # 5: any char followed by liquid and mute consonant, exceptions for 'r+l' and 't+l'
    ((?:(?:[bcdfghjklmnñpqstvy][hlr])|(?:[bcdfghjklmnñpqrstvy][hr])|(?:[bcdfghjklmnñpqrstvyz][h]))[aáeéiíoóuúü])|
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
    #11: any char
    ([a-záéíóúñ])
""", re.I | re.U | re.VERBOSE)  # re.VERBOSE is needed to be able to catch the regex group

"""
Rhythmical Analysis
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

# Words starting with prefixes SIN-/DES- followed by consonant "destituir"
PREFIX_DES_WITH_CONSONANT_RE = (re.compile("^(des)([bcdfgjklmhnñpqrstvxyz].*)", re.I | re.U))

# Words starting with prefixes SIN-/DES- followed by consonant "sinhueso"
PREFIX_SIN_WITH_CONSONANT_RE = (re.compile("^(sin)([bcdfgjklmhnñpqrstvxyz].*)", re.I | re.U))

# Group rh + u[aeiou] diphthongs : "marhuenda"
PREFIX_RNH_DIPHTHONG_RE = (re.compile("(.*?r)(hu[aeioáéíó].*)", re.I | re.U))

# Group consonant+[hlr] with exceptions for ll
CONSONANT_GROUP = (re.compile("(.*[hmnqsw])([hlr][aeiouáéíóú].*)", re.I | re.U))
CONSONANT_GROUP_EXCEPTION_LL = (re.compile("(.*[hlmnqsw])([hr][aeiouáéíóú].*)", re.I | re.U))
CONSONANT_GROUP_EXCEPTION_DL = (re.compile("(.*[d])([l][aeiouáéíóú].*)", re.I | re.U))

# Group vowel+ w + vowel
W_VOWEL_GROUP = (re.compile("(.*[aeiouáéíóú])(w[aeiouáéíóú].*)", re.I | re.U))

# Post-syllabification exceptions for consonant clusters and diphthongs

# Consonant cluster. Example: 'cneorácea'
CONSONANT_CLUSTER_RE = (re.compile(
    "(?:(.*-)|^)([mpgc])-([bcdfghjklmñnpqrstvwxyz][aeioáéíó].*)", re.I | re.U))

# Lowering diphthong. Example: 'ahijador'
LOWERING_DIPHTHONGS_WITH_H = (
    re.compile(
        "((?:.*-|^)(?:qu|[bcdfghjklmñnpqrstvwxyz]+)?)([aeo])-(h[iu](?![aeoiuíúáéó]).*)", re.I | re.U))

# Lowering diphthong. Example: 'buhitiho'
RAISING_DIPHTHONGS_WITH_H = (
    re.compile(
        "((?:.*-|^)(?:qu|[bcdfghjklmñnpqrstvwxyz]+)?)([iu])-(h[aeiouáéó](?![aeoáéiuíú]).*)", re.I | re.U))


"""
Rhythmical Analysis functions
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


def get_synalephas(sinaeresis_words):
    """
    Gets a list of dictionaries for each word on each line of the poem
    and joins the syllables to create phonologic syllables according to its
    'has_synaloepha' value
    :param sinaeresis_words: List of dictionaries for each word of the poem
    :return: A list of conjoined syllables
    """
    prosodic_line = []
    word_list = copy.deepcopy(sinaeresis_words)  # create a deepcopy since we're going to pop()
    for idx, syllables_list in enumerate(word_list):
        for syllable in syllables_list:
            if not syllable.get('has_synalepha'):
                prosodic_line.append(syllable)
            else:
                next_syllable = word_list[idx + 1].pop(0)
                prosodic_line.append({
                    'is_stressed': (syllable.get('is_stressed') or next_syllable.get('is_stressed')),
                    'syllable': "".join([syllable.get('syllable'), next_syllable.get('syllable')]),
                    'has_synalepha': True})
    return prosodic_line


def get_sinaeresis(words_dictionary):
    """
    Gets a list of dictionaries for each word on each line of the poem
    and joins the syllables to create phonological syllables according to its
    'has_sinaeresis' value
    :param words_dictionary: List of dictionaries for each word of the poem
    :return: A list of conjoined syllables
    """
    sinaeresis_words = words_dictionary[:]  # create a copy since we're going to pop()
    phonological_syllables = []
    for idx, key in enumerate(sinaeresis_words):
        if not key.get('has_sinaeresis'):
            phonological_syllables.append(sinaeresis_words[idx])
        else:
            next_syl = sinaeresis_words.pop(idx + 1)
            phonological_syllables.append({
                'is_stressed': (key['is_stressed'] or next_syl['is_stressed']),
                'syllable': "".join([key['syllable'], next_syl['syllable']]),
                'has_sinaeresis': True})
    return phonological_syllables


def get_rhythmical_pattern(line, rhythm_format="indexed"):
    """
    Gets a rhythm pattern for a poem in either "pattern": "-++-+-+-"
    or "index": [1,2,4,6] format
    :param line: a dictionary with the information of the poem
    :param rhythm_format: The output format for the rhythm
    :return: Dictionary with with rhythm and phonologic groups
    """
    rhythm_dict = {}
    rhythmical_stress = ""
    token_list = line['tokens']
    sinaeresis_tokens = {'sinaeresis_tokens': []}
    phonological_groups = {'phonological_groups': []}
    for token in token_list:
        if token.get('word'):
            sinaeresis_tokens['sinaeresis_tokens'].append(get_sinaeresis(token.get('word')))
    synalepha_token_list = get_synalephas(sinaeresis_tokens['sinaeresis_tokens'])
    for token in synalepha_token_list:
        if token.get('syllable'):
            phonological_groups['phonological_groups'].append(token)
    for syllable in synalepha_token_list:
        if syllable['is_stressed']:
            rhythmical_stress += '+'
        else:
            rhythmical_stress += '-'
    last_word = sinaeresis_tokens['sinaeresis_tokens'][-1]
    last_syllable_stress = last_word[-1].get('is_stressed')
    if last_syllable_stress:
        rhythmical_stress += '-'
    elif len(last_word) >= 3:  # Proparoxytone
        third_from_last_syllable_stress = last_word[-3].get('is_stressed')
        if third_from_last_syllable_stress:
            rhythmical_stress = rhythmical_stress[:-1]
    elif len(last_word) > 3:  # Stress on preantepenultimate syllable
        fourth_from_last_syllable_stress = last_word[-4].get('is_stressed')
        if fourth_from_last_syllable_stress:
            rhythmical_stress = rhythmical_stress[:-1]
    if rhythm_format == 'indexed':
        rhythm_dict = {
            'rhythm': {
                'rhythmical_stress': [
                    match.start() for match in re.finditer(r'\+', rhythmical_stress)]},
            'type': rhythm_format}
    elif rhythm_format == 'pattern':
        rhythm_dict = {
            'rhythm': {
                'rhythmical_stress': rhythmical_stress, 'type': rhythm_format}}
    # Count the number of phonological tokens
    rhythm_dict.update({'rhythmical_length': len(rhythmical_stress)})
    return {**phonological_groups, **rhythm_dict}


"""
Syllabifier functions
"""


def apply_exception_rules(word):
    """
    Applies presyllabification rules to a word, based on Antonio Ríos Mestre's work
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
    # Group rh followed by u + diphthong
    if PREFIX_RNH_DIPHTHONG_RE.match(word):
        match = PREFIX_RNH_DIPHTHONG_RE.search(word)
        if match is not None:
            word = "-".join(match.groups())
    return word


def apply_exception_rules_post(word):
    """
    Applies presyllabification rules to a word, based on Antonio Ríos Mestre's work
    :param word: A string to be checked for exceptions
    :return: A string with the presyllabified word
    """
    # We make one pass for every match found so we can perform several substitutions
    if CONSONANT_CLUSTER_RE.search(word):
        for match in CONSONANT_CLUSTER_RE.findall(word)[0]:
            word = re.sub(CONSONANT_CLUSTER_RE, r'\1\2\3', word)
    if LOWERING_DIPHTHONGS_WITH_H.search(word):
        for match in LOWERING_DIPHTHONGS_WITH_H.findall(word)[0]:
            word = re.sub(LOWERING_DIPHTHONGS_WITH_H, r'\1\2\3', word)
    if RAISING_DIPHTHONGS_WITH_H.search(word):
        for match in RAISING_DIPHTHONGS_WITH_H.findall(word)[0]:
            word = re.sub(RAISING_DIPHTHONGS_WITH_H, r'\1\2\3', word)
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
                output += "-" if m.lastindex not in set([5, 8, 11]) else ""
            word = word[1:]
        output = apply_exception_rules_post(output)
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
    :return: Dict with [original syllab word, stressed syllab. word, negative index position of stressed syllable or 0
    if not stressed]
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


def get_scansion(text, rhyme_analysis=False, rhythm_format="pattern"):
    """
    Generates a list of dictionaries for each line
    :param text: Full text to be analyzed
    :param rhyme_analysis: Specify if rhyme analysis is to be performed
    :param rhythm_format: output format for rhythm analysis
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
    for line in lines:
        line.update(get_rhythmical_pattern(line, rhythm_format))
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
    return lines
