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

from spinn_utilities.unigue_list import UnigueList


def test_basic():
    ul = UnigueList()
    ul.append(1)
    ul.append(4)
    ul.append(1)
    assert(ul == [1, 4])


def test_insert():
    ul = UnigueList([0, 1, 2, 3, 4, 5])
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
    assert(type(ul) == UnigueList)


def test_extend():
    ul = UnigueList([0, 1, 2, 3, 4, 5])
    ul.extend([3, 1, 6, 7, 8, 9, 7, 4])
    assert(ul == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    ul += [6, 10, 11]
    assert(ul == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    assert(type(ul) == UnigueList)


def test_add():
    ul = UnigueList([0, 1, 2, 3, 4, 5])
    ul2 = ul + [3, 1, 6, 7, 8, 9, 7, 4]
    assert(ul2 == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    assert(type(ul2) == UnigueList)
    l2 = [3, 1, 6, 7, 8, 9, 7, 4] + ul
    assert(l2 == [3, 1, 6, 7, 8, 9, 7, 4, 0, 1, 2, 3, 4, 5])
    assert(type(l2) == list)


def test_copy():
    ul = UnigueList([0, 1, 2, 3, 4, 5])
    nl = ul.copy()
    assert(type(nl) == UnigueList)
    ul.append(8)
    assert(nl == [0, 1, 2, 3, 4, 5])


def test_standard_ops():
    ul = UnigueList([4, 6, 3, 1, 7])
    ul.reverse()
    assert(ul == [7, 1, 3, 6, 4])
    b = ul.pop()
    assert(ul == [7, 1, 3, 6])
    assert(b == 4)
    ul.sort()
    assert(ul == [1, 3, 6, 7])
    assert(type(ul) == UnigueList)
