from spinn_utilities.ranged.range_dictionary import RangeDictionary
from spinn_utilities.ranged.ranged_list import RangedList


defaults = {"a": "alpha", "b": "bravo"}

rd = RangeDictionary(10, defaults)


def test_ids():
    assert [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] == rd.ids()


def test_value():
    assert "alpha" == rd["a"].get_value_all()
    assert "bravo" == rd["b"].get_value_all()
    assert "a" in rd
    assert "c" not in rd
    assert rd.has_key("b")  # noqa: W601
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
    assert "alpha" == rd1["a"].get_value_all()
    rd1["a"] = "Foo"
    assert "Foo" == rd1["a"].get_value_all()


def test_ranges_by_key():
    rd1 = RangeDictionary(10, defaults)
    assert [(0, 10, "alpha")] == rd1.get_ranges(key="a")


def test_iter_values():
    rd1 = RangeDictionary(10, defaults)
    single1 = rd1[4]
    aware = rd1.iter_all_values(key="a", update_save=True)
    fast = rd1.iter_all_values(key="a", update_save=False)
    assert ["alpha", "alpha", "alpha", "alpha", "alpha", "alpha", "alpha",
            "alpha", "alpha", "alpha"] == list(fast)
    single1["a"] = "Foo"
    assert ["alpha", "alpha", "alpha", "alpha", "Foo", "alpha", "alpha",
            "alpha", "alpha", "alpha"] == list(aware)


def test_iter_values_keys():
    rd1 = RangeDictionary(10, defaults)
    aware = rd1.iter_all_values(key=("a", "b"), update_save=True)
    fast = rd1.iter_all_values(key=("b", "a"), update_save=False)
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


def test_ranges_by_key2():
    rd1 = RangeDictionary(10, defaults)
    assert [(0, 10, "alpha")] == rd1.get_ranges(key="a")
    rd1[4]["a"] = "foo"
    assert [(0, 4, "alpha"), (4, 5, "foo"), (5, 10, "alpha")] == \
        rd1.get_ranges(key="a")


def test_ranges_all():
    rd1 = RangeDictionary(10, defaults)
    assert [(0, 10, {"a": "alpha", "b": "bravo"})] == rd1.get_ranges()
    rd1[4]["a"] = "foo"
    assert [(0, 4, {"a": "alpha", "b": "bravo"}),
            (4, 5, {"a": "foo", "b": "bravo"}),
            (5, 10, {"a": "alpha", "b": "bravo"})] == rd1.get_ranges()


def test_set_range():
    rd1 = RangeDictionary(10, defaults)
    rd1["a"] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert list(rd1["a"]) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_set_list():
    rd1 = RangeDictionary(10, defaults)
    rl = RangedList(10, "gamma")
    rd1["g"] = rl
    new_dict = {"a": "alpha", "b": "bravo", "g": "gamma"}
    assert new_dict == rd1.get_value()
