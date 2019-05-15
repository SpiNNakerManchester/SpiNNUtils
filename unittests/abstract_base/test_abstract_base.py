# Copyright (c) 2017-2018 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pytest
from .abstract_has_constraints import AbstractHasConstraints
from .abstract_has_label import AbstractHasLabel
from .abstract_has_id import AbstractHasId
from .grandparent import GrandParent
from .no_label import NoLabel
from .unchecked_bad_param import UncheckedBadParam


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
        from .checked_bad_param import CheckedBadParam
        # This line never reached but there for pep8
        CheckedBadParam()
