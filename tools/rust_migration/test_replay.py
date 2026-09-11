import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from replay import encode, first_difference


def test_map_order_is_irrelevant_but_lists_and_numbers_are_not():
    assert encode({2: 'b', 1: 'a'}) == encode({1: 'a', 2: 'b'})
    assert encode({1, 2}) == encode({2, 1})
    assert first_difference({'ids': [1, 2]}, {'ids': [2, 1]})['path'] == '$.ids[0]'
    assert first_difference({'x': 1}, {'x': 1.0})['path'] == '$.x'
    assert first_difference({'a': 0, 'b': 1}, {'b': 1, 'a': 0}) is None


def test_missing_state_and_events_cannot_be_silently_ignored():
    assert first_difference({'events': [1]}, {'events': []})['path'] == '$.events'
    try:
        encode(object())
    except TypeError:
        pass
    else:
        raise AssertionError('unsupported state was omitted')
