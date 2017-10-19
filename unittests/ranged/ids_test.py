from spinn_utilities.ranged.range_dictionary import RangeDictionary

defaults = {"a": "alpha", "b": "bravo"}

rd = RangeDictionary(10, defaults)

ranged_view = rd[2,3,8]


def test_ids():
    assert [2, 3, 8] == ranged_view.ids()

def test_value():
    assert "alpha" == ranged_view["a"]
    assert "bravo" == ranged_view["b"]
    assert "a" in ranged_view
    assert "c" not in ranged_view
    assert ranged_view.has_key("b")
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
    rd1 = RangeDictionary(10, defaults)
    ranged_view1 = rd1[4:7]
    assert "alpha" == ranged_view1["a"]
    ranged_view1["a"] = "Foo"
    assert "Foo" == ranged_view1["a"]

