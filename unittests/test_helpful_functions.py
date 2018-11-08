import unittests
from spinn_utilities.helpful_functions import (
    get_valid_components, is_singleton)


def test_is_singleton():
    assert is_singleton(35)
    assert is_singleton(False)
    assert is_singleton(0.12)
    assert is_singleton("")
    assert is_singleton('a')
    assert is_singleton("flashy fish")
    assert not is_singleton([1, 2, 3])
    assert not is_singleton({1: 2, 3: 4})
    assert not is_singleton(frozenset([14]))
    assert not is_singleton((43876,))
    assert is_singleton(object())
    assert is_singleton(lambda x: x * 2 + 1)


def test_get_valid_components():
    # WTF is this function doing?!
    d = get_valid_components(unittests.test_helpful_functions, "_c")
    assert len(d) == 3
    assert d['a'] == a_c
    assert d['a_b'] == a_b
    assert d['b'] == b_c


# Support class for test_get_valid_components
class a_b(object):  # noqa: N801
    pass


# Support class for test_get_valid_components
class b_c(object):  # noqa: N801
    pass


# Support class for test_get_valid_components
class a_c(object):  # noqa: N801
    pass
