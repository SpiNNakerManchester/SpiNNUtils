import unittests
from spinn_utilities.helpful_functions import get_valid_components


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
