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

from spinn_utilities.ranged import RangeDictionary

defaults = {"a": "alpha", "b": "bravo"}
rd = RangeDictionary(10, defaults)
single = rd[4]


def test_ids() -> None:
    assert [4] == single.ids()


def test_value() -> None:
    assert "alpha" == single.get_value("a")
    assert "bravo" == single.get_value("b")
    assert "a" in single
    assert "c" not in single
    assert single.has_key("b")  # noqa: W601
    assert {"a", "b"} == set(single.keys())


def test_items() -> None:
    expected = {("a", "alpha"), ("b", "bravo")}
    result = set(single.items())
    assert expected == result


def test_values() -> None:
    expected = {"alpha", "bravo"}
    result = set(single.values())
    assert expected == result


def test_set() -> None:
    rd1 = RangeDictionary(10, defaults)
    single1 = rd1.view_factory([4])
    assert single1.get_value("a") == "alpha"
    single1["a"] = "foo"
    assert single1.get_value("a") == "foo"


def test_iter_values() -> None:
    rd1 = RangeDictionary(10, defaults)
    single1 = rd1[4]
    aware = single1.iter_all_values(key="a", update_safe=False)
    fast = single1.iter_all_values(key="a", update_safe=True)
    assert ["alpha"] == list(fast)
    rd1["a"] = "Foo"
    assert rd1["a"].get_single_value_all() == "Foo"
    assert ["Foo"] == list(aware)


def test_iter_values_keys() -> None:
    rd1 = RangeDictionary(10, defaults)
    single1 = rd1[4]
    aware = single1.iter_all_values(key=("a", "b"), update_safe=False)
    fast = single1.iter_all_values(key=("b", "a"), update_safe=True)
    assert [{'a': 'alpha', 'b': 'bravo'}] == list(fast)
    rd1["a"] = "Foo"
    assert rd1["a"].get_single_value_all() == "Foo"
    assert [{'a': 'Foo', 'b': 'bravo'}] == list(aware)


def test_ranges_by_key() -> None:
    rd1 = RangeDictionary(10, defaults)
    single1 = rd1[4]
    assert [(4, 5, "alpha")] == list(single1.iter_ranges(key="a"))
    single1["a"] = "foo"
    assert [(0, 4, "alpha"), (4, 5, "foo"), (5, 10, "alpha")] == \
        rd1.get_ranges(key="a")
    assert [(4, 5, "foo")] == list(single1.iter_ranges(key="a"))


def test_ranges_all() -> None:
    rd1 = RangeDictionary(10, defaults)
    single1 = rd1[4]
    assert [(4, 5, {"a": "alpha", "b": "bravo"})] == single1.get_ranges()
    single1["a"] = "foo"
    assert [(0, 4, {"a": "alpha", "b": "bravo"}),
            (4, 5, {"a": "foo", "b": "bravo"}),
            (5, 10, {"a": "alpha", "b": "bravo"})] == rd1.get_ranges()
    assert [(4, 5, {"a": "foo", "b": "bravo"})] == \
        single1.get_ranges()


def test_str() -> None:
    s = str(single)
    assert 0 < len(s)
