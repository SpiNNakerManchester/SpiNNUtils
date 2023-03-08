# Copyright (c) 2017 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
    machine_time_step = 1000
    return lambda x: numpy.exp(float(-machine_time_step) / (1000.0 * x))


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
