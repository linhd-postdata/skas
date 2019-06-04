import spacy
from spacy.tokenizer import Tokenizer
from spacy_affixes import AffixesMatcher


def custom_tokenizer(nlp):
    """
    Add custom tokenizer options to the spacy pipeline by adding '-'
    to the list of affixes
    :param nlp: Spacy language model
    :return: New custom tokenizer
    """
    custom_affixes = [r'-']
    prefix_re = spacy.util.compile_prefix_regex(
        list(nlp.Defaults.prefixes) + custom_affixes)
    suffix_re = spacy.util.compile_suffix_regex(
        list(nlp.Defaults.suffixes) + custom_affixes)
    infix_re = spacy.util.compile_infix_regex(
        list(nlp.Defaults.infixes) + custom_affixes)

    return Tokenizer(nlp.vocab, prefix_search=prefix_re.search,
                     suffix_search=suffix_re.search,
                     infix_finditer=infix_re.finditer, token_match=None)


def load_pipeline(lang=None):
    """
    Loads the new pipeline with the custom tokenizer
    :param lang: Spacy language model
    :return: New custom language model
    """
    if lang is None:
        lang = 'es_core_news_md'
    nlp = spacy.load(lang)
    nlp.tokenizer = custom_tokenizer(nlp)
    nlp.remove_pipe("affixes") if nlp.has_pipe("affixes") else None
    nlp.add_pipe(AffixesMatcher(nlp), name="affixes", first=True)
    return nlp
