from spinn_utilities.ranged.range_dictionary import RangeDictionary

defaults = {"a": "alpha", "b": "bravo"}

rd = RangeDictionary(10, defaults)

single = rd[4]


def test_ids():
    assert [4] == single.ids()


def test_value():
    assert "alpha" == single["a"]
    assert "bravo" == single["b"]
    assert "a" in single
    assert "c" not in single
    assert single.has_key("b")
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
    single1 = rd1[4]
    assert single1["a"] == "alpha"
    single1["a"] = "foo"
    assert single1["a"] == "foo"

def test_iter_values():
    rd1 = RangeDictionary(10, defaults)
    single1 = rd1[4]
    aware = single1.iter_values("a", fast = False)
    fast = single1.iter_values("a", fast = True)
    assert ["alpha"] == list(fast)
    rd1["a"] = "Foo"
    assert rd1["a"] == "Foo"
    assert ["Foo"] == list(aware)
