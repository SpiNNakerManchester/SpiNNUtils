from spinn_utilities.ranged.range_dictionary import RangeDictionary

defaults = {"a": "alpha", "b": "bravo"}

rd = RangeDictionary(10, defaults)

slice_view = rd[4:6]


def test_ids():
    assert [4, 5] == slice_view.ids()

def test_value():
    assert "alpha" == slice_view["a"]
    assert "bravo" == slice_view["b"]
    assert "a" in slice_view
    assert "c" not in slice_view
    assert slice_view.has_key("b")
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
    ranged_view1 = rd1[4:7]
    assert "alpha" == ranged_view1["a"]
    ranged_view1["a"] = "Foo"
    assert "Foo" == ranged_view1["a"]


def test_iter_values():
    rd1 = RangeDictionary(10, defaults)
    ranged_view1 = rd1[4:7]
    aware = ranged_view1.iter_values("a", fast = False)
    fast = ranged_view1.iter_values("a", fast = True)
    assert ["alpha","alpha","alpha"] == list(fast)
    rd1["a"] = "Foo"
    assert rd1["a"] == "Foo"
    assert ["Foo","Foo","Foo"] == list(aware)
