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
import numpy
from spinn_utilities.ranged import MultipleValuesException
from spinn_utilities.ranged import RangedList


def test_simple() -> None:
    rl: RangedList = RangedList(10, "a")
    ranges = rl.get_ranges()
    assert list(rl) == ["a", "a", "a", "a", "a", "a", "a", "a", "a", "a"]
    assert len(ranges) == 1
    assert ranges[0][0] == 0
    assert ranges[0][1] == 10
    assert ranges[0][2] == "a"
    assert rl[3] == "a"


def test_get_slice() -> None:
    rl: RangedList = RangedList(10, "a")
    assert ["a", "a"] == rl[2:4]
    rl[3:5] = "b"
    assert ["a", "b"] == rl[2:4]


def test_insert_id() -> None:
    rl: RangedList = RangedList(10, "a")
    rl[4] = "b"
    assert "b" == rl[4]
    assert "a" == rl[3]
    ranges = rl.get_ranges()
    assert list(rl) == ["a", "a", "a", "a", "b", "a", "a", "a", "a", "a"]
    assert ranges == [(0, 4, "a"), (4, 5, "b"), (5, 10, "a")]
    rl[5] = "b"
    assert list(rl) == ["a", "a", "a", "a", "b", "b", "a", "a", "a", "a"]
    ranges = rl.get_ranges()
    assert ranges == [(0, 4, "a"), (4, 6, "b"), (6, 10, "a")]


def test_insert_slice_part_range() -> None:
    rl: RangedList = RangedList(10, "a")
    assert "b" not in rl
    rl[4:6] = "b"
    assert "b" in rl
    ranges = rl.get_ranges()
    assert list(rl) == ["a", "a", "a", "a", "b", "b", "a", "a", "a", "a"]
    assert ranges == [(0, 4, "a"), (4, 6, "b"), (6, 10, "a")]
    assert "a" in rl
    assert "c" not in rl
    assert ["a", "b"] == rl[3:5]


def test_insert_complex_slice() -> None:
    rl: RangedList = RangedList(10, "a")
    assert rl[4:8:2] == ["a", "a"]
    assert "b" not in rl
    rl[4:8:2] = "b"
    assert "b" in rl
    assert list(rl) == ["a", "a", "a", "a", "b", "a", "b", "a", "a", "a"]
    ranges = rl.get_ranges()
    assert ranges == [(0, 4, "a"), (4, 5, "b"), (5, 6, "a"), (6, 7, "b"),
                      (7, 10, "a")]
    assert "a" in rl
    assert "c" not in rl
    assert ["a", "b"] == rl[3:7:3]


def test_insert_slice_up_to() -> None:
    rl: RangedList = RangedList(10, "a")
    rl[3:7] = "b"
    assert rl.get_ranges() == [(0, 3, "a"), (3, 7, "b"), (7, 10, "a")]
    rl[1:3] = "c"
    assert list(rl) == ["a", "c", "c", "b", "b", "b", "b", "a", "a", "a"]
    assert rl.get_ranges() == [(0, 1, "a"), (1, 3, "c"), (3, 7, "b"),
                               (7, 10, "a")]


def test_insert_slice_start_over_lap_to() -> None:
    rl: RangedList = RangedList(10, "a")
    rl[3:7] = "b"
    assert rl.get_ranges() == [(0, 3, "a"), (3, 7, "b"), (7, 10, "a")]
    rl[1:5] = "c"
    assert list(rl) == ["a", "c", "c", "c", "c", "b", "b", "a", "a", "a"]
    assert rl.get_ranges() == [(0, 1, "a"), (1, 5, "c"), (5, 7, "b"),
                               (7, 10, "a")]


def test_insert_slice_start_over_lap_both() -> None:
    rl: RangedList = RangedList(10, "a")
    rl[3:7] = "b"
    assert rl.get_ranges() == [(0, 3, "a"), (3, 7, "b"), (7, 10, "a")]
    rl[1:8] = "c"
    assert list(rl) == ["a", "c", "c", "c", "c", "c", "c", "c", "a", "a"]
    assert rl.get_ranges() == [(0, 1, "a"), (1, 8, "c"), (8, 10, "a")]


def test_insert_slice_to_previous() -> None:
    rl: RangedList = RangedList(10, "a")
    rl[3:7] = "b"
    assert rl.get_ranges() == [(0, 3, "a"), (3, 7, "b"), (7, 10, "a")]
    rl[2:5] = "a"
    assert list(rl) == ["a", "a", "a", "a", "a", "b", "b", "a", "a", "a"]
    assert rl.get_ranges() == [(0, 5, "a"), (5, 7, "b"), (7, 10, "a")]


def test_insert_slice_to_big() -> None:
    rl: RangedList = RangedList(2, "a")
    rl[1:3] = "b"
    assert rl.get_ranges() == [(0, 1, "a"), (1, 2, "b")]
    assert list(rl) == ["a", "b"]


def test_insert_slice_to_far() -> None:
    rl: RangedList = RangedList(2, "a")
    rl[3:6] = "b"
    assert rl.get_ranges() == [(0, 2, "a")]
    assert list(rl) == ["a", "a"]


def test_insert_slice_inverted() -> None:
    rl: RangedList = RangedList(4, "a")
    rl[2:1] = "b"
    assert rl.get_ranges() == [(0, 4, "a")]


def test_insert_slice_stop_too_negative() -> None:
    rl: RangedList = RangedList(4, "a")
    rl[2:-5] = "b"
    assert rl.get_ranges() == [(0, 4, "a")]


def test_insert_slice_start_too_negative() -> None:
    rl: RangedList = RangedList(4, "a")
    rl[-6:3] = "b"
    assert rl.get_ranges() == [(0, 3, "b"), (3, 4, "a")]


def test_insert_end() -> None:
    rl: RangedList = RangedList(10, "a")
    rl[1] = "b"
    assert rl.get_ranges() == [(0, 1, "a"), (1, 2, "b"), (2, 10, "a")]
    rl[4:6] = "c"
    assert rl.get_ranges() == [(0, 1, "a"), (1, 2, "b"), (2, 4, "a"),
                               (4, 6, "c"), (6, 10, "a")]


def test_insert_list() -> None:
    rl: RangedList = RangedList(10, "a")
    rl[4, 8, 2] = "b"
    assert rl == ["a", "a", "b", "a", "b", "a", "a", "a", "b", "a"]
    assert rl.get_ranges() == [(0, 2, "a"), (2, 3, "b"), (3, 4, "a"),
                               (4, 5, "b"), (5, 8, "a"), (8, 9, "b"),
                               (9, 10, "a")]
    rl[3] = "b"
    assert rl == ["a", "a", "b", "b", "b", "a", "a", "a", "b", "a"]
    assert rl.get_ranges() == [(0, 2, "a"), (2, 5, "b"), (5, 8, "a"),
                               (8, 9, "b"), (9, 10, "a")]
    rl[3] = "x"
    assert rl == ["a", "a", "b", "x", "b", "a", "a", "a", "b", "a"]
    assert rl.get_ranges() == [(0, 2, "a"), (2, 3, "b"), (3, 4, "x"),
                               (4, 5, "b"), (5, 8, "a"), (8, 9, "b"),
                               (9, 10, "a")]
    assert rl.count("b") == 3


def test_iter_simple() -> None:
    rl: RangedList = RangedList(10, "a")
    for i in range(10):
        rl[i] = i
    assert rl == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_iter_complex() -> None:
    rl: RangedList = RangedList(size=10, value="a", key="alpha")
    list_iter = rl.iter()
    assert "a" == next(list_iter)  # 0
    assert "a" == next(list_iter)  # 1
    assert "a" == next(list_iter)  # 2
    rl[1] = "b"
    assert "a" == next(list_iter)  # 3
    rl[4:6] = "c"
    assert "c" == next(list_iter)  # 4
    assert "c" == next(list_iter)  # 5
    assert "a" == next(list_iter)  # 6


def test_iter() -> None:
    rl: RangedList = RangedList(size=10, value="a", key="alpha")
    it = rl.iter()
    assert list(it) == ["a", "a", "a", "a", "a", "a", "a", "a", "a", "a"]


def test_ranges_by_id() -> None:
    rl: RangedList = RangedList(size=10, value="a", key="alpha")
    assert [(3, 4, "a")] == list(rl.iter_ranges_by_id(3))


def test_ranges_by_slice() -> None:
    rl: RangedList = RangedList(size=10, value="a", key="alpha")
    assert [(3, 8, "a")] == list(rl.iter_ranges_by_slice(3, 8))
    rl[5] = "foo"
    rl[5] = "foo"
    assert [(3, 5, "a"), (5, 6, "foo"), (6, 8, "a")] == \
        list(rl.iter_ranges_by_slice(3, 8))


def test_ranges_by_ids() -> None:
    rl: RangedList = RangedList(size=10, value="a", key="alpha")
    assert [(1, 4, "a"), (7, 8, "a"), (4, 5, "a")] == \
        list(rl.iter_ranges_by_ids((1, 2, 3, 7, 4)))
    rl[6] = "foo"
    assert [(1, 4, "a"), (7, 8, "a"), (4, 5, "foo")] == \
        list(rl.iter_ranges_by_ids((1, 2, 3, 7, 4)))
    rl[3] = "foo"
    assert [(1, 3, "a"), (3, 4, "foo"), (7, 8, "a"), (4, 5, "a")] == \
        list(rl.iter_ranges_by_ids((1, 2, 3, 7, 4)))


def test_iter_by_slice() -> None:
    rl: RangedList = RangedList(size=10, value="a", key="alpha")
    assert ["a", "a", "a"] == list(rl.iter_by_slice(2, 5))
    rl[3:7] = "b"
    assert ["a", "b", "b"] == list(rl.iter_by_slice(2, 5))


def test_update_slice_with_list() -> None:
    rl: RangedList = RangedList(size=10, value="a", key="alpha")
    rl[2:5] = [2, 3, 4]
    assert ["a", "a", 2, 3, 4, "a", "a", "a", "a", "a"] == rl


def test_iter_by_ids() -> None:
    rl: RangedList = RangedList(size=10, value="a", key="alpha")
    rl[5:10] = "b"
    assert rl[5:10] == ["b", "b", "b", "b", "b"]
    assert rl[0:5] == ["a", "a", "a", "a", "a"]
    assert list(rl.iter_by_ids([9, 1, 2, 5])) == ["b", "a", "a", "b"]


def test_iter_by_numpy() -> None:
    rl: RangedList = RangedList(size=10, value="a", key="alpha")
    first = numpy.array([0, 1, 2, 3, 4])
    second = numpy.array([5, 6, 7, 8, 9])
    rl[second] = "b"
    assert rl[second] == ["b", "b", "b", "b", "b"]
    assert rl[first] == ["a", "a", "a", "a", "a"]
    weird = numpy.array([9, 1, 2, 5])
    assert list(rl.iter_by_ids(weird)) == ["b", "a", "a", "b"]


def test_set_value_by_slice() -> None:
    rl: RangedList = RangedList(size=10, value="a", key="alpha")
    rl.set_value_by_slice(2, 7, "b")
    assert rl == ["a", "a", "b", "b", "b", "b", "b", "a", "a", "a"]
    rl.set_value_by_slice(3, 7, "c")
    assert rl == ["a", "a", "b", "c", "c", "c", "c", "a", "a", "a"]
    rl.set_value_by_slice(5, 8, "d")
    assert rl == ["a", "a", "b", "c", "c", "d", "d", "d", "a", "a"]
    rl.set_value_by_slice(4, 6, "c")
    assert rl == ["a", "a", "b", "c", "c", "c", "d", "d", "a", "a"]


def test_set_value_by_callable() -> None:
    rl: RangedList = RangedList(size=10, value="a", key="alpha")
    rl.set_value(lambda x: x * 2)
    assert list(rl) == [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
    rl.set_value_by_slice(4, 6, lambda x: x * 3)
    assert list(rl) == [0, 2, 4, 6, 12, 15, 12, 14, 16, 18]
    rl.set_value_by_ids([1, 8, 2], lambda x: x * 4)
    assert list(rl) == [0, 4, 8, 6, 12, 15, 12, 14, 32, 18]


def test_bad_callable() -> None:
    rl: RangedList = RangedList(size=10, value="a", key="alpha")
    with pytest.raises(TypeError):
        rl.set_value(lambda: 2)
    with pytest.raises(TypeError):
        rl.set_value(lambda x, y: x * y)
    with pytest.raises(TypeError):
        rl.set_value(lambda x: len(x))


def test_index() -> None:
    rl: RangedList = RangedList(size=10, value="a", key="alpha")
    rl[6] = "b"
    assert rl.index("b") == 6
    with pytest.raises(ValueError):
        assert rl.index("not there") == "Oops there anyway"


def test_slice_by_list() -> None:
    rl: RangedList = RangedList(size=5, value="a", key="alpha")
    assert rl == ["a", "a", "a", "a", "a"]
    rl[2:4] = ["b", "c"]
    assert rl == ["a", "a", "b", "c", "a"]
    assert rl[2:4] == ["b", "c"]


def test_set_ids__with_list() -> None:
    rl: RangedList = RangedList(size=5, value="a", key="alpha")
    rl.set_value_by_ids([2, 1, 4], ["b", "c", "d"])
    assert rl == ["a", "c", "b", "a", "d"]


def test_no_size() -> None:
    rl: RangedList = RangedList(value=["a", "b", "c"])
    assert rl == ["a", "b", "c"]


def test_bad_no_size() -> None:
    with pytest.raises(ValueError):
        RangedList(value=35)


def test_high_id() -> None:
    rl: RangedList = RangedList(value=["a", "b", "c"])
    with pytest.raises(IndexError):
        print(rl[7])
    with pytest.raises(IndexError):
        rl.get_value_by_id(7)


def test_bad_ids() -> None:
    rl: RangedList = RangedList(value=["a", "b", "c"])
    with pytest.raises(IndexError):
        print(rl[4])
    with pytest.raises(IndexError):
        rl.get_value_by_id(-1)
    with pytest.raises(TypeError):
        rl.get_value_by_id("a")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        rl.get_value_by_id(None)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        print(rl["a"])  # type: ignore[index, arg-type]
    with pytest.raises(TypeError):
        print(rl[2.3])


def test_str() -> None:
    rl: RangedList = RangedList(value=["a", "b", "c"])
    assert str(["a", "b", "c"]) == str(rl)


def test_get_single_value() -> None:
    rl: RangedList = RangedList(value=["a", "a", "a"])
    assert "a" == rl.get_single_value_by_slice(0, 2)


def test_too_many() -> None:
    rl: RangedList = RangedList(value=["a", "b", "c"])
    with pytest.raises(MultipleValuesException):
        rl.get_single_value_all()
    with pytest.raises(MultipleValuesException):
        rl.get_single_value_by_slice(0, 2)


def test_slice_by_selector() -> None:
    rl: RangedList = RangedList(size=5, value=[0, 1, 2, 3, 4], key="alpha")
    assert rl.get_values(slice(2, 3)) == [2]
    assert rl.get_values(slice(2, 4)) == [2, 3]


def test_negative_id() -> None:
    rl: RangedList = RangedList(size=5, value=[0, 1, 2, 3, 4], key="alpha")
    assert rl.get_values(-2) == [3]
    rl[-2] = 13
    assert rl[3] == 13
    assert rl[-2] == 13


def test_bad_selector() -> None:
    rl: RangedList = RangedList(size=5, value=[0, 1, 2, 3, 4], key="alpha")
    with pytest.raises(TypeError):
        rl.get_values(34.23)


def test_two_many_values_slice() -> None:
    rl: RangedList = RangedList(size=5, value=1, key="alpha")
    rl[2] = 2
    with pytest.raises(MultipleValuesException):
        rl.get_single_value_by_slice(1, 3)
    with pytest.raises(MultipleValuesException):
        rl.get_single_value_by_ids([1, 2])


def test_iter_by_slice_ranged() -> None:
    rl: RangedList = RangedList(size=15, value=1, key="alpha")
    rl[2] = 2
    rl[12] = 2
    assert [1, 2] == list(rl.iter_by_slice(11, 13))


def test_as_list_bad() -> None:
    with pytest.raises(Exception):
        RangedList.as_list([1, 2, 3], 4)  # type: ignore


def test_range_merge() -> None:
    rl: RangedList = RangedList(size=5, value=1, key="alpha")
    assert [(0, 5, 1)] == rl.get_ranges()
    rl[2: 4] = 2
    assert [(0, 2, 1), (2, 4, 2), (4, 5, 1)] == rl.get_ranges()
    rl[2: 4] = 1
    assert [(0, 5, 1)] == rl.get_ranges()


def test_no_default() -> None:
    rl: RangedList = RangedList(value=[1, 2, 3])
    assert rl.get_default() is None


def test_get_values_all() -> None:
    rl: RangedList = RangedList(value=[1, 2, 3])
    assert [1, 2, 3] == rl.get_values()


def test_get_values_complex_slice() -> None:
    rl: RangedList = RangedList(value=range(10))
    assert [2, 4, 6] == rl.get_values(slice(-8, -3, 2))


def test_get_values_list() -> None:
    rl: RangedList = RangedList(value=range(10))
    assert [2, 6, 4] == rl.get_values([2, 6, 4])


def test_get_values_mask() -> None:
    rl: RangedList = RangedList(value=["a", "b", "c", "d", "e"])
    assert ["a", "c", "e"] == rl.get_values(
        [True, False, True, False, True])
    assert ["a", "c", "e"] == rl.get_values(
        [True, False, True, False, True, True])
    assert ["a", "c"] == rl.get_values(
        [True, False, True, False])


def test_get_values_bad_lists() -> None:
    rl: RangedList = RangedList(value=range(10))
    with pytest.raises(TypeError):
        rl.get_values([2, -1, 4])
    with pytest.raises(TypeError):
        rl.get_values([2, 12, 4])
    with pytest.raises(TypeError):
        rl.get_values([2, True])
    with pytest.raises(TypeError):
        rl.get_values([2, "True"])  # type: ignore[list-item]


def test_selector_to_ids() -> None:
    rl: RangedList = RangedList(value=range(5))
    assert [0, 1, 2, 3, 4] == list(rl.selector_to_ids(None))
    assert [0, 1] == list(rl.selector_to_ids(slice(2)))
    assert [2] == list(rl.selector_to_ids(2))
    with pytest.raises(TypeError):
        rl.selector_to_ids(-7)
    with pytest.raises(TypeError):
        rl.selector_to_ids(7)


def test_warn() -> None:
    rl: RangedList = RangedList(value=range(5))
    assert [0, 1, 2] == rl.selector_to_ids([True, True, True, False],
                                           warn=True)
    assert [0, 1, 2] == rl.selector_to_ids(
        [True, True, True, False, False, False], warn=True)
    assert [0, 1, 2, 3, 4] == list(rl.selector_to_ids(None, warn=True))


def test_numpy_selector() -> None:
    rl: RangedList = RangedList(value=range(5))
    selector = numpy.array([1, 3, 4])
    assert [1, 3, 4] == rl.selector_to_ids(selector)
