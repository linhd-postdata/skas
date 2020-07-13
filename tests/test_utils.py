# -*- coding: utf-8 -*-
from rantanplan.utils import argcount
from rantanplan.utils import generate_exceeded_offset_indices


def test_generate_exceeded_offset_indices():
    values = [0, 1, 2, 1, 3, 3, 4, 4, 1, 1, 3, 3]
    out = [8, 10]
    assert list(generate_exceeded_offset_indices(values)) == out


def test_argcount():
    values = [0, 1, 2, 1, 3, 3, 4, 4, 1, 1, 3, 3]
    out = [0, 2]
    assert argcount(values, count=1) == out
