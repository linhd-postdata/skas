# -*- coding: utf-8 -*-
from collections import Counter


def generate_exceeded_offset_indices(values, offset=4):
    """Yield the indices of the duplicated elements
    at offset + 1 positions from their previous one; or None if none found.
    For example, for an offset of 4 and a list of values as follows
    [0, 1, 2, 1, 3, 3, 4, 4, 1, 1, 3, 3]
                             ↓     ↓
                             8     10
    It will yield the indices 8 and 10.
    """
    positions = {}
    for index, code in enumerate(values):
        if code in positions and index - positions[code] > offset:
            yield index
        positions[code] = index


def argcount(values, count=1):
    """Return the indices of elements that appear count times in values"""
    return [value for value, value_count in Counter(values).items()
            if value_count == count]
