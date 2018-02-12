import pytest

from spinn_utilities.ranged.range_dictionary import RangeDictionary
from spinn_utilities.ranged.single_view import _SingleView


defaults = {"a": "alpha", "b": "bravo"}

rd = RangeDictionary(10, defaults)

slice_view = rd[4:6]


def test_ids():
    assert [4, 5] == slice_view.ids()


def test_value():
    assert "alpha" == slice_view.get_value("a")
    assert "bravo" == slice_view.get_value("b")
    assert "a" in slice_view
    assert "c" not in slice_view
    assert slice_view.has_key("b")  # noqa: W601
    assert {"a", "b"} == set(slice_view.keys())


def test_items():
    expected = {("a", "alpha"), ("b", "bravo")}
    result = set(slice_view.items())
    assert expected == result


def test_values():
    expected = {"alpha", "bravo"}
    result = set(slice_view.values())
    assert expected == result


def test_set_range_direct():
    rd1 = RangeDictionary(10, defaults)
    slice_view1 = rd1[4:7]
    assert "alpha" == slice_view1.get_value("a")
    slice_view1["a"] = "Foo"
    assert "Foo" == slice_view1.get_value("a")


def test_iter_values():
    rd1 = RangeDictionary(10, defaults)
    slice_view1 = rd1[4:7]
    aware = slice_view1.iter_all_values("a", update_save=False)
    fast = slice_view1.iter_all_values("a", update_save=True)
    assert ["alpha", "alpha", "alpha"] == list(fast)
    rd1["a"] = "Foo"
    assert rd1["a"].get_value_all() == "Foo"
    assert ["Foo", "Foo", "Foo"] == list(aware)


def test_ranges_by_key():
    rd1 = RangeDictionary(10, defaults)
    slice_view1 = rd1[4:7]
    assert [(4, 7, "alpha")] == list(slice_view1.iter_ranges(key="a"))
    slice_view1["a"] = "foo"
    assert [(0, 4, "alpha"), (4, 7, "foo"), (7, 10, "alpha")] \
        == rd1.get_ranges(key="a")
    assert [(4, 7, "foo")] == list(slice_view1.iter_ranges(key="a"))
    rd1[5]["a"] = "bar"
    assert [(4, 5, "foo"), (5, 6, "bar"), (6, 7, "foo")] \
        == list(slice_view1.iter_ranges(key="a"))


def test_ranges_all():
    rd1 = RangeDictionary(10, defaults)
    slice_view1 = rd1[4:7]
    assert [(4, 7, {"a": "alpha", "b": "bravo"})] == \
        list(slice_view1.iter_ranges())
    slice_view1["a"] = "foo"
    assert [(0, 4, {"a": "alpha", "b": "bravo"}),
            (4, 7, {"a": "foo", "b": "bravo"}),
            (7, 10, {"a": "alpha", "b": "bravo"})] \
        == rd1.get_ranges()
    assert [(4, 7, {"a": "foo", "b": "bravo"})] == \
        list(slice_view1.iter_ranges())
    rd1[5]["a"] = "bar"
    assert [(4, 5, {"a": "foo", "b": "bravo"}),
            (5, 6, {"a": "bar", "b": "bravo"}),
            (6, 7, {"a": "foo", "b": "bravo"})] == \
        list(slice_view1.iter_ranges())


def test_left_slice():
    slice_view1 = rd[4:]
    assert [(4, 10, {"a": "alpha", "b": "bravo"})] == \
        list(slice_view1.iter_ranges())


def test_right_slice():
    slice_view1 = rd[:4]
    assert [(0, 4, {"a": "alpha", "b": "bravo"})] == \
        list(slice_view1.iter_ranges())


def test_minus_slice():
    slice_view1 = rd[-8:-4]
    assert [(2, 6, {"a": "alpha", "b": "bravo"})] == \
        list(slice_view1.iter_ranges())


def test_empty_slice():
    with pytest.raises(Exception):
        print rd[2: 2]


def test_one_slice():
    slice_view1 = rd[2: 3]
    assert isinstance(slice_view1, _SingleView)


def test_str():
    s = str(slice_view)
    assert 0 < len(s)


def test_iter_by_slice():
    rd1 = RangeDictionary(10)
    rd1["g"] = "gamma"
    rd1["a"] = "alpha"
    rd1["b"] = ["bravo0", "bravo1", "bravo2", "bravo3", "bravo4", "bravo5",
                "bravo6", "bravo7", "bravo8+", "bravo9"]

    slice_view1 = rd1[2: 4]
    iterator = slice_view1.iter_all_values()
    assert {"a": "alpha", "b": "bravo2", "g": "gamma"} == iterator.next()
    assert {"a": "alpha", "b": "bravo3", "g": "gamma"} == iterator.next()
    with pytest.raises(StopIteration):
        assert "OVERFLOW" == iterator.next()

    iterator = slice_view1.iter_all_values(update_save=True)
    assert {"a": "alpha", "b": "bravo2", "g": "gamma"} == iterator.next()
    rd1["b"][3] = "new3"
    assert {"a": "alpha", "b": "new3", "g": "gamma"} == iterator.next()
    with pytest.raises(StopIteration):
        assert "OVERFLOW" == iterator.next()
    rd1["b"][3] = "bravo3"

    iterator = slice_view1.iter_all_values(key="b")
    assert "bravo2" == iterator.next()
    assert "bravo3" == iterator.next()
    with pytest.raises(StopIteration):
        assert "OVERFLOW" == iterator.next()

    iterator = slice_view1.iter_all_values(update_save=True, key="b")
    assert "bravo2" == iterator.next()
    rd1["b"][3] = "new3"
    assert "new3" == iterator.next()
    with pytest.raises(StopIteration):
        assert "OVERFLOW" == iterator.next()
    rd1["b"][3] = "bravo3"

    iterator = rd1.iter_values_by_slice(2, 4, key=["b", "a"])
    assert {"a": "alpha", "b": "bravo2"} == iterator.next()
    assert {"a": "alpha", "b": "bravo3"} == iterator.next()
    with pytest.raises(StopIteration):
        assert "OVERFLOW" == iterator.next()

    iterator = rd1.iter_values_by_slice(
        2, 4, key=["b", "a"], update_save=True)
    assert {"a": "alpha", "b": "bravo2"} == iterator.next()
    rd1["b"][3] = "new3"
    assert {"a": "alpha", "b": "new3"} == iterator.next()
    with pytest.raises(StopIteration):
        assert "OVERFLOW" == iterator.next()
    rd1["b"][3] = "bravo3"
