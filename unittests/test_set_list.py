# Copyright (c) 2020 The University of Manchester
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
from spinn_utilities.set_list import SetList


def test_create():
    o = SetList()
    assert o is not None


def test_set_ness():
    o = SetList()
    assert len(o) == 0
    o.add(123)
    assert len(o) == 1
    o.add(123)
    assert len(o) == 1
    o.add(456)
    assert len(o) == 2
    o.add(456)
    assert len(o) == 2
    o.add(123)
    assert len(o) == 2
    assert o == set([123, 456])
    assert o == set([456, 123])
    assert o == [123, 456]
    assert o != [456, 123]
    o.remove(123)
    assert len(o) == 1
    o.remove(456)
    assert len(o) == 0
    with pytest.raises(KeyError):  # @UndefinedVariable
        o.remove(789)
    o.discard(789)
    assert len(o) == 0
    o.add(789)
    assert len(o) == 1
    assert 789 in o
    o.discard(789)
    assert 789 not in o
    assert len(o) == 0


def test_ordered_ness():
    o = SetList()
    o.add(12)
    o.add(78)
    o.add(56)
    o.add(34)
    o.add(90)
    assert len(o) == 5
    assert list(o) == [12, 78, 56, 34, 90]
    result = []
    for item in o:
        result.append(item)
    assert result == [12, 78, 56, 34, 90]


def test_containment():
    o = SetList()
    o.add(12)
    o.add(78)
    o.add(56)
    o.add(34)
    o.add(90)
    for item in [12, 78, 56, 34, 90]:
        assert item in o
    for item in [123, 456, 789]:
        assert item not in o


def test_repr():
    o = SetList()
    o.add(12)
    o.add(78)
    o.add(56)
    o.add(34)
    o.add(90)
    s = "{}".format(o)
    assert s == "SetList([12, 78, 56, 34, 90])"


def test_pop():
    o = SetList()
    o.add(12)
    o.add(78)
    o.add(56)
    o.add(34)
    o.add(90)
    for item in [90, 34, 56, 78, 12]:
        assert o.pop() == item
    with pytest.raises(KeyError):  # @UndefinedVariable
        o.pop()


def test_update():
    o = SetList()
    o.add(1)
    o.add(2)
    o.add(3)
    o.update([3, 4, 5])
    for item in (5, 4, 3, 2, 1):
        assert o.pop() == item
    with pytest.raises(KeyError):
        o.pop()


def test_obscure_stuff():
    o = SetList()
    o.add(1)
    o.add(2)
    o.add(3)
    assert [x for x in reversed(o)] == [3, 2, 1]
    o2 = SetList(o)
    assert [x for x in o2] == [1, 2, 3]
    assert o == o2
    o2 |= [4]
    assert o != o2
    assert repr(SetList()) == "SetList()"


def test_peek():
    o = SetList()
    o.add(1)
    o.add(2)
    o.add(3)
    p1 = o.peek()
    assert p1 == 3

def test_basic():
    ul = SetList()
    ul.append(1)
    ul.append(4)
    ul.append(1)
    assert(ul == [1, 4])


def test_insert():
    ul = SetList([0, 1, 2, 3, 4, 5])
    # Add value in
    ul[4] = 6
    assert(ul == [0, 1, 2, 3, 6, 4, 5])
    ul[4] = 2
    assert(ul == [0, 1, 3, 6, 2, 4, 5])
    ul[1] = 6
    ul.insert(1, 6)
    assert(ul == [0, 6, 1, 3, 2, 4, 5])
    ul.insert(2, 7)
    assert(ul == [0, 6, 7, 1, 3, 2, 4, 5])
    assert(type(ul) == SetList)


def test_extend():
    ul = SetList([0, 1, 2, 3, 4, 5])
    ul.extend([3, 1, 6, 7, 8, 9, 7, 4])
    assert(ul == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    ul += [6, 10, 11]
    assert(ul == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    assert(type(ul) == SetList)


def test_add():
    ul = SetList([0, 1, 2, 3, 4, 5])
    ul2 = ul + [3, 1, 6, 7, 8, 9, 7, 4]
    assert(ul2 == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    assert(type(ul2) == SetList)
    l2 = [3, 1, 6, 7, 8, 9, 7, 4] + ul
    assert(l2 == [3, 1, 6, 7, 8, 9, 7, 4, 0, 1, 2, 3, 4, 5])
    assert(type(l2) == list)


def test_copy():
    ul = SetList([0, 1, 2, 3, 4, 5])
    nl = ul.copy()
    assert(type(nl) == SetList)
    ul.append(8)
    assert(nl == [0, 1, 2, 3, 4, 5])


def test_standard_ops():
    ul = SetList([4, 6, 3, 1, 7])
    ul.reverse()
    assert(ul == [7, 1, 3, 6, 4])
    b = ul.pop()
    assert(ul == [7, 1, 3, 6])
    assert(b == 4)
    ul.sort()
    assert(ul == [1, 3, 6, 7])
    assert(type(ul) == SetList)
