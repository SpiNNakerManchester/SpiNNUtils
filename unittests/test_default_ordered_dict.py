# Copyright (c) 2019 The University of Manchester
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

import copy
import pickle
import pytest
from spinn_utilities.default_ordered_dict import DefaultOrderedDict
from spinn_utilities.ordered_set import OrderedSet


def test_standard_default():
    o = DefaultOrderedDict(None)
    assert o is not None
    o["bar"] = 2
    with pytest.raises(KeyError):  # @UndefinedVariable
        x = o["FOO"]
        assert x is None
    assert o["bar"] == 2


def test_list_default():
    o = DefaultOrderedDict(list)
    assert o is not None
    o["bar"] = 2
    assert isinstance(o["FOO"], list)
    o["gamma"].append("beacon")
    assert o["bar"] == 2


def test_ordered_set_default():
    o = DefaultOrderedDict(OrderedSet)
    assert o is not None
    o["foo"].add(2)
    o["foo"].add(1)
    assert 2 in o["foo"]
    assert 1 not in o["bar"]


def test_keys_in_order():
    o = DefaultOrderedDict(lambda: bytes(b"abc"))
    a = o["a"]
    b = o["b"]
    c = o["c"]
    assert a == b == c
    assert tuple(o) == ("a", "b", "c")


def test_callable():
    try:
        DefaultOrderedDict("Not callable")
        assert False
    except TypeError:
        pass


def test_special_methods():
    o = DefaultOrderedDict(list)
    o["gamma"].append("bacon")
    # test _-reduce
    pickle.dumps(o)
    # test copy
    o2 = o.copy()
    assert o2["gamma"] == ["bacon"]
    o3 = copy.deepcopy(o)
    assert o3["gamma"] == ["bacon"]
    a = repr(o)
    b = repr(o3)
    assert a == b
