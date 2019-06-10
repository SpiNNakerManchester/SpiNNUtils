import pytest
from spinn_utilities.ranged import RangeDictionary

defaults = {"a": "alpha", "b": "bravo"}
rd = RangeDictionary(10, defaults)
ranged_view = rd[2, 3, 8]


def test_ids():
    assert [2, 3, 8] == ranged_view.ids()


def test_value():
    assert "alpha" == ranged_view.get_value("a")
    assert "bravo" == ranged_view.get_value("b")
    assert "a" in ranged_view
    assert "c" not in ranged_view
    assert ranged_view.has_key("b")  # noqa: W601
    assert {"a", "b"} == set(ranged_view.keys())


def test_items():
    expected = {("a", "alpha"), ("b", "bravo")}
    result = set(ranged_view.items())
    assert expected == result


def test_values():
    expected = {"alpha", "bravo"}
    result = set(ranged_view.values())
    assert expected == result


def test_set_range_direct():
    ranged_view1 = rd[2, 3, 8]
    assert "alpha" == ranged_view1.get_value("a")
    ranged_view1["a"] = "Foo"
    assert "Foo" == ranged_view1.get_value("a")


def test_iter_values():
    rd1 = RangeDictionary(10, defaults)
    ranged_view1 = rd1[2, 3, 8]
    aware = ranged_view1.iter_all_values("a", update_save=False)
    fast = ranged_view1.iter_all_values("a", update_save=True)
    assert ["alpha", "alpha", "alpha"] == list(fast)
    rd1["a"] = "Foo"
    assert rd1["a"][0] == "Foo"
    assert ["Foo", "Foo", "Foo"] == list(aware)


def test_ranges_by_key():
    rd1 = RangeDictionary(10, defaults)
    view = rd1[1, 2, 4, 5, 6, 7]
    view["a"] = "foo"
    assert [(0, 1, "alpha"), (1, 3, "foo"), (3, 4, "alpha"), (4, 8, "foo"),
            (8, 10, "alpha")] == list(rd1.iter_ranges(key="a"))
    assert [(1, 3, "foo"), (4, 8, "foo")] == list(view.iter_ranges(key="a"))
    rd1[5]["a"] = "bar"
    assert [(1, 3, "foo"), (4, 5, "foo"), (5, 6, "bar"), (6, 8, "foo")] \
        == list(view.iter_ranges(key="a"))


def test_ranges_by_all():
    rd1 = RangeDictionary(10, defaults)
    view = rd1[1, 2, 4, 5, 6, 7]
    view["a"] = "foo"
    assert [(0, 1, {"a": "alpha", "b": "bravo"}),
            (1, 3, {"a": "foo", "b": "bravo"}),
            (3, 4, {"a": "alpha", "b": "bravo"}),
            (4, 8, {"a": "foo", "b": "bravo"}),
            (8, 10, {"a": "alpha", "b": "bravo"})] == rd1.get_ranges()
    assert [(1, 3, {"a": "foo", "b": "bravo"}),
            (4, 8, {"a": "foo", "b": "bravo"})] == view.get_ranges()
    rd1[5]["a"] = "bar"
    assert [(1, 3, {"a": "foo", "b": "bravo"}),
            (4, 5, {"a": "foo", "b": "bravo"}),
            (5, 6, {"a": "bar", "b": "bravo"}),
            (6, 8, {"a": "foo", "b": "bravo"})] \
        == view.get_ranges()


def test_get_str():
    with pytest.raises(KeyError):
        assert ranged_view["OOPS"]


def test_no_set():
    with pytest.raises(KeyError):
        ranged_view[3] = "Better not be allowed"
    with pytest.raises(KeyError):
        ranged_view[rd] = "Can not do this either!"


def test_defaults():
    assert "alpha" == ranged_view.get_default("a")


def test_str():
    s = str(ranged_view)
    assert len(s) > 0
