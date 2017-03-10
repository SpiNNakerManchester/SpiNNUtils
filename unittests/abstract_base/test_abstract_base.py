import pytest

from spinn_utilities.overrides import overrides

from abstract_grandparent import AbstractGrandParent
from abstract_has_constraints import AbstractHasConstraints
from abstract_has_label import AbstractHasLabel
from abstract_has_id import AbstractHasId
# CheckedBadParam import throws and exception
from grandparent import GrandParent
from no_label import NoLabel
from unchecked_bad_param import UncheckedBadParam


def test_create():
    o = GrandParent()
    assert o is not None
    assert isinstance(o, AbstractHasLabel)
    assert isinstance(o, AbstractHasConstraints)
    assert isinstance(o, GrandParent)
    assert not isinstance(o, AbstractHasId)


def test_no_has_label():
    with pytest.raises(TypeError):
        o = NoLabel()


# What this test checks is actually undesirable but it shows it happens
def test_unchecked_bad_param():
    o = UncheckedBadParam()
    assert o is not None


def test_checked_bad_param():
    with pytest.raises(AttributeError):
        from checked_bad_param import CheckedBadParam

