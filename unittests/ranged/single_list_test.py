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

from spinn_utilities.ranged import RangedList, SingleList


def test_simple():
    a_list = RangedList(5, 12, "twelve")
    single = SingleList(a_list=a_list, operation=lambda x: x + 5)
    assert single == [17, 17, 17, 17, 17]


def test_muliple():
    a_list = RangedList(5, 12, "twelve")
    q = 2
    single = SingleList(a_list=a_list, operation=lambda x: x / q)
    assert list(single) == [6, 6, 6, 6, 6]
    a_list[1] = 6
    a_list[2] = 3.0
    a_list[3] = 8
    assert single == [6, 3, 1.5, 4, 6]


def create_lambda():
    import numpy
    default_machine_time_step = 1000
    return lambda x: numpy.exp(
        float(-default_machine_time_step) / (1000.0 * x))


def test_complex():
    a_list = RangedList(5, 20, "twenty")
    single = SingleList(a_list=a_list, operation=create_lambda())
    assert single == [0.95122942450071402, 0.95122942450071402,
                      0.95122942450071402, 0.95122942450071402,
                      0.95122942450071402]


def test_get_value():
    a_list = RangedList(5, 20, "twenty")
    single = SingleList(a_list=a_list, operation=create_lambda())
    assert single[2] == 0.95122942450071402
    assert single.get_single_value_by_slice(2, 4) == 0.95122942450071402
    assert single.get_single_value_by_ids([2, 4]) == 0.95122942450071402


def test_apply_operation():
    a_list = RangedList(5, 20, "twenty")
    single = a_list.apply_operation(operation=create_lambda())
    assert single[2] == 0.95122942450071402


def test_get_slice():
    a_list = RangedList(5, 12, "twelve")
    single = SingleList(a_list=a_list, operation=lambda x: x / 3)
    a_list[1:3] = 6
    assert single[2:4] == [2, 4]


def test_ranges():
    a_list = RangedList(5, 12, "twelve")
    single = SingleList(a_list=a_list, operation=lambda x: x / 3)
    a_list[1:3] = 6
    assert [(0, 1, 4), (1, 3, 2), (3, 5, 4)] == list(single.iter_ranges())


def test_ranges_by_slice():
    a_list = RangedList(5, 12, "twelve")
    single = SingleList(a_list=a_list, operation=lambda x: x / 3)
    a_list[1:3] = 6
    assert [(2, 3, 2), (3, 4, 4)] == list(single.iter_ranges_by_slice(2, 4))


def test_get_ids():
    a_list = RangedList(5, 12, "twelve")
    single = SingleList(a_list=a_list, operation=lambda x: x / 3)
    assert single[1:5:2] == [4, 4]
    a_list[1:3] = 6
    assert single[1:5:2] == [2, 4]


def test_iter_by_slice():
    a_list = RangedList(5, 12, "twelve")
    single = SingleList(a_list=a_list, operation=lambda x: x / 3)
    assert [4, 4, 4] == list(single.iter_by_slice(2, 5))
    a_list[:3] = 6
    assert [2, 4, 4] == list(single.iter_by_slice(2, 5))
    a_list[4:] = 24
    assert [2, 4, 8] == list(single.iter_by_slice(2, 5))


def test_equals():
    a_list = RangedList(5, 12, "twelve")
    double = SingleList(a_list=a_list, operation=lambda x: x * 2)
    half_double = SingleList(a_list=double, operation=lambda x: x / 2)
    assert a_list == half_double


def test_defaults():
    a_list = RangedList(5, 12, "twelve")
    assert a_list.get_default() == 12
    double = SingleList(a_list=a_list, operation=lambda x: x * 2)
    assert double.get_default() == 24
