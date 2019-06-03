import spacy

from rantanplan.pipeline import load_pipeline

test_dict_list = [
    {'text': 'esto', 'pos_': '', 'tag_': '', '_.line': 0, '_.has_tmesis': False,
     'lower_': 'esto', 'n_rights': 0},
    {'text': 'es', 'pos_': '', 'tag_': '', '_.line': 0, '_.has_tmesis': False,
     'lower_': 'es', 'n_rights': 0},
    {'text': 'una', 'pos_': '', 'tag_': '', '_.line': 0, '_.has_tmesis': False,
     'lower_': 'una', 'n_rights': 0},
    {'text': 'prue-\nba', 'pos_': '', 'tag_': '', '_.line': 0,
     '_.has_tmesis': True, 'lower_': 'prue-\nba',
     'n_rights': 0}]


def test_load_pipeline(monkeypatch):
    def mockreturn(lang=None):
        return spacy.blank('es')

    monkeypatch.setattr(spacy, 'load', mockreturn)
    nlp = load_pipeline()
    doc = nlp("esto es una prue-\nba")
    token_dict = []
    for token in doc:
        token_dict.append(
            {"text": token.text, "pos_": token.pos_, "tag_": token.tag_,
             "_.line": token._.line, "_.has_tmesis": token._.has_tmesis,
             "lower_": token.lower_, "n_rights": token.n_rights})  # noqa
    assert token_dict == test_dict_list
