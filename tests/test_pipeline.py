import spacy

from rantanplan.pipeline import load_pipeline

test_dict_list = [
    {'text': 'prue', 'pos_': '', 'tag_': '',
     'n_rights': 0},
    {'text': '-', 'pos_': '', 'tag_': '',
     'n_rights': 0},
    {'text': '\n', 'pos_': '', 'tag_': '',
     'n_rights': 0},
    {'text': 'ba', 'pos_': '', 'tag_': '',
     'n_rights': 0}]


def test_load_pipeline(monkeypatch):
    def mockreturn(lang=None):
        return spacy.blank('es')

    monkeypatch.setattr(spacy, 'load', mockreturn)
    nlp = load_pipeline()
    doc = nlp("prue-\nba")
    token_dict = []
    for token in doc:
        token_dict.append(
            {"text": token.text, "pos_": token.pos_, "tag_": token.tag_,
            "n_rights": token.n_rights})  # noqa
    assert token_dict == test_dict_list
