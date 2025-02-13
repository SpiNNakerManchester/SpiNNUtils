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

import pytest
from spinn_utilities.ranged import RangedList, DualList
import numpy


def test_simple() -> None:
    numerator: RangedList = RangedList(5, 10, "ten")
    divisor: RangedList = RangedList(5, 5, "five")
    div = numerator / divisor
    assert div == [2, 2, 2, 2, 2]


def test_muliple() -> None:
    numerator: RangedList = RangedList(5, 12.0, "numerator")
    divisor: RangedList = RangedList(5, 4, "divisor")
    div = numerator / divisor
    assert div == [3, 3, 3, 3, 3]
    divisor[1] = 6
    divisor[2] = 3
    divisor[3] = 8
    assert div == [3, 2, 4, 1.5, 3]


def test_complex() -> None:
    numerator: RangedList = RangedList(5, 12.0, "numerator")
    divisor: RangedList = RangedList(5, 4, "divisor")
    div = numerator / divisor
    assert list(div) == [3, 3, 3, 3, 3]
    divisor[1:3] = 6
    numerator[2, 4] = 24
    assert div == [3, 2, 4, 3, 6]


def test_get_value() -> None:
    numerator: RangedList = RangedList(5, 12.0, "numerator")
    divisor: RangedList = RangedList(5, 4, "divisor")
    div = numerator / divisor
    assert div.get_single_value_by_slice(1, 3) == 3
    assert div.get_single_value_by_ids([1, 3]) == 3
    divisor[1:3] = 6
    numerator[2, 4] = 24
    assert div[2] == 4


def test_get_slice() -> None:
    numerator: RangedList = RangedList(5, 12.0, "numerator")
    divisor: RangedList = RangedList(5, 4, "divisor")
    div = numerator / divisor
    divisor[1:3] = 6
    numerator[2, 4] = 24
    assert div[2:4] == [4, 3]


def test_ranges() -> None:
    numerator: RangedList = RangedList(10, 12.0, "numerator")
    divisor: RangedList = RangedList(10, 4, "divisor")
    div = numerator / divisor
    divisor[1:6] = 6
    numerator[4:8] = 24
    assert [(0, 1, 3.0), (1, 4, 2.0), (4, 6, 4), (6, 8, 6), (8, 10, 3.0)] == \
        list(div.iter_ranges())


def test_ranges_by_slice() -> None:
    numerator: RangedList = RangedList(10, 12.0, "numerator")
    divisor: RangedList = RangedList(10, 4, "divisor")
    div = numerator / divisor
    divisor[1:6] = 6
    numerator[4:8] = 24
    assert [(2, 4, 2.0), (4, 6, 4), (6, 7, 6)] == \
        list(div.iter_ranges_by_slice(2, 7))


def test_get_ids() -> None:
    numerator: RangedList = RangedList(5, 12.0, "numerator")
    divisor: RangedList = RangedList(5, 4, "divisor")
    div = numerator / divisor
    divisor[1:3] = 6
    numerator[2, 4] = 24
    assert div[1:5:2] == [2, 3]


def test_both_ranges_iter() -> None:
    left: RangedList = RangedList(10, 10.0, "ten")
    left[3] = 20
    right: RangedList = RangedList(10, 4, "four")
    dual = DualList(left=left, right=right, operation=lambda x, y: x+y)
    assert [14, 24, 14, 14] == list(dual.iter_by_slice(2, 6))


def test_left_list_ranges_iter() -> None:
    left: RangedList = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], "many")
    right: RangedList = RangedList(10, 10, "ten")
    dual = DualList(left=left, right=right, operation=lambda x, y: x+y)
    assert [12, 13, 14, 15] == list(dual.iter_by_slice(2, 6))


def test_right_list_ranges_iter() -> None:
    right: RangedList = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], "many")
    left: RangedList = RangedList(10, 10, "ten")
    dual = DualList(left=left, right=right, operation=lambda x, y: x+y)
    assert [12, 13, 14, 15] == list(dual.iter_by_slice(2, 6))


def test_both_list_ranges_iter() -> None:
    left: RangedList = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], "many")
    right: RangedList = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], "many")
    dual = DualList(left=left, right=right, operation=lambda x, y: x+y)
    assert [4, 6, 8, 10] == list(dual.iter_by_slice(2, 6))


def test_add_number() -> None:
    left: RangedList = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], "many")
    right: RangedList = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], "many")
    add = left + 4
    assert [6, 7, 8, 9] == list(add.iter_by_slice(2, 6))
    add = left + right
    assert [0, 2, 4, 6, 8, 10, 12, 14, 16, 18] == add
    with pytest.raises(Exception):
        left + "foo"  # type: ignore[operator]


def test_sub_number() -> None:
    left: RangedList = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], "many")
    right: RangedList = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], "many")
    sub = left - 4
    assert [-2, -1, 0, 1] == list(sub.iter_by_slice(2, 6))
    sub = left - right
    assert [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] == sub
    with pytest.raises(Exception):
        left - "foo"  # type: ignore[operator]


def test_mult_number() -> None:
    left: RangedList = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], "many")
    right: RangedList = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], "many")
    mult = left * 4
    assert [8, 12, 16, 20] == list(mult.iter_by_slice(2, 6))
    mult = left * right
    assert [0, 1, 4, 9, 16, 25, 36, 49, 64, 81] == mult
    with pytest.raises(Exception):
        left * "foo"  # type: ignore[operator]


def test_div_number() -> None:
    left: RangedList = RangedList(4, [0, 6, 12, 24], "many")
    right: RangedList = RangedList(4, [1, 2, 3, 4], "many")
    ans = left / 6
    assert [0, 1, 2, 4] == ans
    ans = left / right
    assert [0, 3, 4, 6] == ans
    with pytest.raises(Exception):
        left / "foo"  # type: ignore[operator]
    with pytest.raises(ZeroDivisionError):
        left / 0


def test_floor_div_number() -> None:
    left: RangedList = RangedList(4, [0, 6, 12, 24], "many")
    right: RangedList = RangedList(4, [1, 2, 3, 4], "many")
    ans = left // 6
    assert [0, 1, 2, 4] == ans
    ans = left // right
    assert [0, 3, 4, 6] == ans
    with pytest.raises(Exception):
        left // "foo"  # type: ignore[operator]
    with pytest.raises(ZeroDivisionError):
        left // 0


def test_get_default() -> None:
    left: RangedList = RangedList(4, 3, "three")
    assert 3 == left.get_default()
    right: RangedList = RangedList(4, 2, "two")
    add = left + right
    result = add.get_default()
    assert 5 == result


def test_both_equals() -> None:
    left: RangedList = RangedList(4, 3, "three")
    right: RangedList = RangedList(4, 2, "two")
    add = left + right
    simple: RangedList = RangedList(4, 5, "five")
    assert add == simple
    left[1] = 7
    simple[1] = 9
    assert add == simple


def test_dif_size() -> None:
    left: RangedList = RangedList(3, 3, "three")
    right: RangedList = RangedList(2, 2, "two")
    with pytest.raises(Exception):
        left + right


def test_numpy_array() -> None:
    left: RangedList = RangedList(2, numpy.array([2, 4, 6]), "many",
                                  use_list_as_value=True)
    right: RangedList = RangedList(2, 2, "many")
    ans = left / right
    value = ans.get_single_value_all()
    assert isinstance(value, numpy.ndarray)
    assert all(value == numpy.array([1, 2, 3]))
