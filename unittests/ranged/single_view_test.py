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

from spinn_utilities.ranged import RangeDictionary

defaults = {"a": "alpha", "b": "bravo"}
rd = RangeDictionary(10, defaults)
single = rd[4]


def test_ids():
    assert [4] == single.ids()


def test_value():
    assert "alpha" == single.get_value("a")
    assert "bravo" == single.get_value("b")
    assert "a" in single
    assert "c" not in single
    assert single.has_key("b")  # noqa: W601
    assert {"a", "b"} == set(single.keys())


def test_items():
    expected = {("a", "alpha"), ("b", "bravo")}
    result = set(single.items())
    assert expected == result


def test_values():
    expected = {"alpha", "bravo"}
    result = set(single.values())
    assert expected == result


def test_set():
    rd1 = RangeDictionary(10, defaults)
    single1 = rd1.view_factory([4])
    assert single1.get_value("a") == "alpha"
    single1["a"] = "foo"
    assert single1.get_value("a") == "foo"


def test_iter_values():
    rd1 = RangeDictionary(10, defaults)
    single1 = rd1[4]
    aware = single1.iter_all_values(key="a", update_save=False)
    fast = single1.iter_all_values(key="a", update_save=True)
    assert ["alpha"] == list(fast)
    rd1["a"] = "Foo"
    assert rd1["a"].get_single_value_all() == "Foo"
    assert ["Foo"] == list(aware)


def test_iter_values_keys():
    rd1 = RangeDictionary(10, defaults)
    single1 = rd1[4]
    aware = single1.iter_all_values(key=("a", "b"), update_save=False)
    fast = single1.iter_all_values(key=("b", "a"), update_save=True)
    assert [{'a': 'alpha', 'b': 'bravo'}] == list(fast)
    rd1["a"] = "Foo"
    assert rd1["a"].get_single_value_all() == "Foo"
    assert [{'a': 'Foo', 'b': 'bravo'}] == list(aware)


def test_ranges_by_key():
    rd1 = RangeDictionary(10, defaults)
    single1 = rd1[4]
    assert [(4, 5, "alpha")] == list(single1.iter_ranges(key="a"))
    single1["a"] = "foo"
    assert [(0, 4, "alpha"), (4, 5, "foo"), (5, 10, "alpha")] == \
        rd1.get_ranges(key="a")
    assert [(4, 5, "foo")] == list(single1.iter_ranges(key="a"))


def test_ranges_all():
    rd1 = RangeDictionary(10, defaults)
    single1 = rd1[4]
    assert [(4, 5, {"a": "alpha", "b": "bravo"})] == single1.get_ranges()
    single1["a"] = "foo"
    assert [(0, 4, {"a": "alpha", "b": "bravo"}),
            (4, 5, {"a": "foo", "b": "bravo"}),
            (5, 10, {"a": "alpha", "b": "bravo"})] == rd1.get_ranges()
    assert [(4, 5, {"a": "foo", "b": "bravo"})] == \
        single1.get_ranges()


def test_str():
    s = str(single)
    assert 0 < len(s)
