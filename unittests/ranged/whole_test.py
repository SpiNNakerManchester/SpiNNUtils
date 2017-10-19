from spinn_utilities.ranged.range_dictionary import RangeDictionary

defaults = {"a": "alpha", "b": "bravo"}

rd = RangeDictionary(10, defaults)

def test_ids():
    assert [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] == rd.ids()

def test_value():
    assert "alpha" == rd["a"]
    assert "bravo" == rd["b"]
    assert "a" in rd
    assert "c" not in rd
    assert rd.has_key("b")
    assert {"a", "b"} == set(rd.keys())


def test_items():
    expected = {("a", "alpha"), ("b", "bravo")}
    result = set(rd.items())
    assert expected == result


def test_values():
    expected = {"alpha", "bravo"}
    result = set(rd.values())
    assert expected == result


def test_set_range_direct():
    rd1 = RangeDictionary(10, defaults)
    assert "alpha" == rd1["a"]
    rd1["a"] = "Foo"
    assert "Foo" == rd1["a"]

