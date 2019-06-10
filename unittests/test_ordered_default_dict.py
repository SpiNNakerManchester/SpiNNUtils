import pytest
from spinn_utilities.ordered_default_dict import DefaultOrderedDict
from spinn_utilities.ordered_set import OrderedSet


def test_standard_default():
    o = DefaultOrderedDict()
    assert o is not None
    o["bar"] = 2
    with pytest.raises(KeyError):  # @UndefinedVariable
        o["FOO"]
    assert o["bar"] == 2


def test_list_default():
    o = DefaultOrderedDict(list)
    assert o is not None
    o["bar"] = 2
    assert isinstance(o["FOO"], list)
    o["gamma"].append("beacon")
    assert o["bar"] == 2


def test_orderedset_default():
    o = DefaultOrderedDict(OrderedSet)
    assert o is not None
    o["foo"].add(2)
    o["foo"].add(1)
    assert 2 in o["foo"]
    assert 1 not in o["bar"]
