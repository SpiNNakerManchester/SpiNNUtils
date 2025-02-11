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
from spinn_utilities.ranged import RangeDictionary, RangedList

defaults = {"a": "alpha", "b": "bravo"}
rd = RangeDictionary(10, defaults)


def test_ids() -> None:
    assert [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] == list(rd.ids())


def test_value() -> None:
    assert "alpha" == rd["a"].get_single_value_all()
    assert "bravo" == rd["b"].get_single_value_all()
    assert "a" in rd
    assert "c" not in rd
    assert rd.has_key("b")  # noqa: W601
    assert {"a", "b"} == set(rd.keys())


def test_items() -> None:
    expected = {("a", "alpha"), ("b", "bravo")}
    result = set(rd.items())
    assert expected == result


def test_values() -> None:
    expected = {"alpha", "bravo"}
    result = set(rd.values())
    assert expected == result


def test_set_range_direct() -> None:
    rd1 = RangeDictionary(10, defaults)
    assert "alpha" == rd1["a"].get_single_value_all()
    rd1["a"] = "Foo"
    assert "Foo" == rd1["a"].get_single_value_all()


def test_ranges_by_key() -> None:
    rd1 = RangeDictionary(10, defaults)
    assert [(0, 10, "alpha")] == rd1.get_ranges(key="a")


def test_iter_values() -> None:
    rd1 = RangeDictionary(10, defaults)
    single1 = rd1[4]
    aware = rd1.iter_all_values(key="a", update_safe=True)
    fast = rd1.iter_all_values(key="a", update_safe=False)
    assert ["alpha", "alpha", "alpha", "alpha", "alpha", "alpha", "alpha",
            "alpha", "alpha", "alpha"] == list(fast)
    single1["a"] = "Foo"
    assert ["alpha", "alpha", "alpha", "alpha", "Foo", "alpha", "alpha",
            "alpha", "alpha", "alpha"] == list(aware)


def test_iter_values_keys() -> None:
    rd1 = RangeDictionary(10, defaults)
    aware = rd1.iter_all_values(key=("a", "b"), update_safe=True)
    fast = rd1.iter_all_values(key=("b", "a"), update_safe=False)
    assert [{'a': 'alpha', 'b': 'bravo'}, {'a': 'alpha', 'b': 'bravo'},
            {'a': 'alpha', 'b': 'bravo'}, {'a': 'alpha', 'b': 'bravo'},
            {'a': 'alpha', 'b': 'bravo'}, {'a': 'alpha', 'b': 'bravo'},
            {'a': 'alpha', 'b': 'bravo'}, {'a': 'alpha', 'b': 'bravo'},
            {'a': 'alpha', 'b': 'bravo'}, {'a': 'alpha', 'b': 'bravo'}] \
        == list(fast)
    rd1[4]["a"] = "Foo"
    rd1[6]["b"] = "Bar"
    assert [{'a': 'alpha', 'b': 'bravo'}, {'a': 'alpha', 'b': 'bravo'},
            {'a': 'alpha', 'b': 'bravo'}, {'a': 'alpha', 'b': 'bravo'},
            {'a': 'Foo', 'b': 'bravo'}, {'a': 'alpha', 'b': 'bravo'},
            {'a': 'alpha', 'b': 'Bar'}, {'a': 'alpha', 'b': 'bravo'},
            {'a': 'alpha', 'b': 'bravo'}, {'a': 'alpha', 'b': 'bravo'}] \
        == list(aware)


def test_ranges_by_key2() -> None:
    rd1 = RangeDictionary(10, defaults)
    assert [(0, 10, "alpha")] == rd1.get_ranges(key="a")
    rd1[4]["a"] = "foo"
    assert [(0, 4, "alpha"), (4, 5, "foo"), (5, 10, "alpha")] == \
        rd1.get_ranges(key="a")


def test_ranges_all() -> None:
    rd1 = RangeDictionary(10, defaults)
    assert [(0, 10, {"a": "alpha", "b": "bravo"})] == rd1.get_ranges()
    rd1[4]["a"] = "foo"
    assert [(0, 4, {"a": "alpha", "b": "bravo"}),
            (4, 5, {"a": "foo", "b": "bravo"}),
            (5, 10, {"a": "alpha", "b": "bravo"})] == rd1.get_ranges()


def test_set_range() -> None:
    rd1: RangeDictionary = RangeDictionary(10, defaults)
    rd1["a"] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert rd1["a"] == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_set_list() -> None:
    rd1 = RangeDictionary(10, defaults)
    rl: RangedList = RangedList(10, "gamma")
    rd1["g"] = rl
    new_dict = {"a": "alpha", "b": "bravo", "g": "gamma"}
    assert new_dict == rd1.get_value()


def test_empty() -> None:
    rd1: RangeDictionary = RangeDictionary(10)
    rl: RangedList = RangedList(10, "gamma")
    rd1["g"] = rl
    rd1["a"] = "alpha"
    rd1["b"] = ["bravo", "bravo", "bravo", "bravo", "bravo", "bravo", "bravo",
                "bravo", "bravo", "bravo"]
    new_dict = {"a": "alpha", "b": "bravo", "g": "gamma"}
    assert new_dict == rd1.get_value()


def test_iter_tests() -> None:
    rd1: RangeDictionary = RangeDictionary(10)
    rl: RangedList = RangedList(10, "gamma")
    rd1["g"] = rl
    rd1["a"] = "alpha"
    rd1["b"] = ["bravo", "bravo", "bravo", "bravo", "bravo", "bravo", "bravo",
                "bravo", "bravo", "bravo"]
    result = set(rd1.iteritems())
    check1 = {('a', 'alpha'), ('b', 'bravo'), ('g', 'gamma')}
    assert check1 == result
    result = set(rd1.itervalues())
    check2 = {'alpha', 'bravo', 'gamma'}
    assert check2 == result


def test_contains() -> None:
    rd1: RangeDictionary = RangeDictionary(10)
    rl: RangedList = RangedList(10, "gamma")
    rd1["g"] = rl
    rd1["a"] = "alpha"
    rd1["b"] = ["bravo", "bravo", "bravo", "bravo", "bravo", "bravo", "bravo",
                "bravo", "bravo", "bravo"]
    assert "a" in rd1
    assert "alpha" not in rd1
    assert 1 in rd1
    assert 14 not in rd1
    with pytest.raises(KeyError):
        assert (rl in rd1)  # type: ignore[operator]


def test_reset() -> None:
    rd1: RangeDictionary = RangeDictionary(10)
    rl: RangedList = RangedList(10, "gamma")
    rd1["g"] = rl
    rd1["a"] = "alpha"
    rd1["b"] = ["bravo", "bravo", "bravo", "bravo", "bravo", "bravo", "bravo",
                "bravo", "bravo", "bravo"]
    rd1["a"] = "beta"
    rd1.reset("a")
    assert rd1["a"] == ["alpha", "alpha", "alpha", "alpha", "alpha", "alpha",
                        "alpha", "alpha", "alpha", "alpha"]


def test_bad_set() -> None:
    rd1: RangeDictionary = RangeDictionary(10)
    with pytest.raises(KeyError):
        rd1[2] = "This should not work"  # type: ignore[index]
    with pytest.raises(KeyError):
        rd1[rd] = "This should not work"  # type: ignore[index]


def test_iter_by_slice() -> None:
    rd1: RangeDictionary = RangeDictionary(10)
    rl: RangedList = RangedList(10, "gamma")
    rd1["g"] = rl
    rd1["a"] = "alpha"
    rd1["b"] = ["bravo0", "bravo1", "bravo2", "bravo3", "bravo4", "bravo5",
                "bravo6", "bravo7", "bravo8+", "bravo9"]

    iterator = rd1.iter_values_by_slice(2, 4)
    assert {"a": "alpha", "b": "bravo2", "g": "gamma"} == next(iterator)
    assert {"a": "alpha", "b": "bravo3", "g": "gamma"} == next(iterator)
    with pytest.raises(StopIteration):
        next(iterator)

    iterator = rd1.iter_values_by_slice(2, 4, update_safe=True)
    assert {"a": "alpha", "b": "bravo2", "g": "gamma"} == next(iterator)
    rd1["b"][3] = "new3"
    assert {"a": "alpha", "b": "new3", "g": "gamma"} == next(iterator)
    with pytest.raises(StopIteration):
        next(iterator)
    rd1["b"][3] = "bravo3"

    iterator = rd1.iter_values_by_slice(2, 4, key="b")
    assert "bravo2" == next(iterator)
    assert "bravo3" == next(iterator)
    with pytest.raises(StopIteration):
        next(iterator)

    iterator = rd1.iter_values_by_slice(2, 4, key="b", update_safe=True)
    assert "bravo2" == next(iterator)
    rd1["b"][3] = "new3"
    assert "new3" == next(iterator)
    with pytest.raises(StopIteration):
        assert "OVERFLOW" == next(iterator)
    rd1["b"][3] = "bravo3"

    iterator = rd1.iter_values_by_slice(2, 4, key=["b", "a"])
    assert {"a": "alpha", "b": "bravo2"} == next(iterator)
    assert {"a": "alpha", "b": "bravo3"} == next(iterator)
    with pytest.raises(StopIteration):
        next(iterator)

    iterator = rd1.iter_values_by_slice(
        2, 4, key=["b", "a"], update_safe=True)
    assert {"a": "alpha", "b": "bravo2"} == next(iterator)
    rd1["b"][3] = "new3"
    assert {"a": "alpha", "b": "new3"} == next(iterator)
    with pytest.raises(StopIteration):
        next(iterator)
    rd1["b"][3] = "bravo3"


def test_defaults() -> None:
    assert "alpha" == rd.get_default("a")
    rd.set_default("a", "newa")
    assert "newa" == rd.get_default("a")


def test_bad_factory() -> None:
    with pytest.raises(KeyError):
        rd.view_factory([1, "a"])   # type: ignore[list-item]


def test_copy() -> None:
    rd: RangeDictionary = RangeDictionary(3)
    a_list1: RangedList = RangedList(3, [1, 2, 3])
    a_list2: RangedList = RangedList(3, 5)
    a_calc1 = a_list1 * 4
    a_calc2 = a_list2 * 4
    rd["list1"] = a_list1
    rd["list2"] = a_list2
    rd["calc1"] = a_calc1
    rd["calc2"] = a_calc2
    rd2 = rd.copy()
    a_list1_copy = rd2["list1"]
    assert a_list1_copy == [1, 2, 3]
    assert list(a_list1_copy.iter_ranges()) == \
           [(0, 1, 1), (1, 2, 2), (2, 3, 3)]
    a_list2_copy = rd2["list2"]
    assert list(a_list2_copy.iter_ranges()) == [(0, 3, 5)]
    assert a_list2_copy == [5, 5, 5]
    calc1_copy = rd2["calc1"]
    assert calc1_copy == [4, 8, 12]
    assert list(calc1_copy.iter_ranges()) == \
           [(0, 1, 4), (1, 2, 8), (2, 3, 12)]
    calc2_copy = rd2["calc2"]
    assert calc2_copy == [20, 20, 20]
    assert list(calc2_copy.iter_ranges()) == [(0, 3, 20)]
