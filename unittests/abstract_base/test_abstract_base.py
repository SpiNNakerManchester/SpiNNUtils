import pytest

from abstract_has_constraints import AbstractHasConstraints
from abstract_has_label import AbstractHasLabel
from abstract_has_id import AbstractHasId
from abstract_no_base_marker import AbstractNoBaseMarker
# CheckedBadParam import throws an exception
from grandparent import GrandParent
from no_base_user import NoBaseUser
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
        NoLabel()


# What this test checks is actually undesirable but it shows it happens
def test_unchecked_bad_param():
    o = UncheckedBadParam()
    assert o is not None


def test_checked_bad_param():
    with pytest.raises(AttributeError):
        from checked_bad_param import CheckedBadParam
        # This line never reached but there for pep8
        CheckedBadParam()

def test_no_base_marker():
    o = NoBaseUser()
    assert isinstance(o, AbstractNoBaseMarker)
