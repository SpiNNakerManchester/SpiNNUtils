import pytest

from spinn_utilities.ranged.range_dictionary import RangeDictionary
from spinn_utilities.ranged.ranged_list import RangedList


defaults = {"a": "alpha", "b": "bravo"}

rd = RangeDictionary(10, defaults)


def test_ids():
    assert [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] == list(rd.ids())


def test_value():
    assert "alpha" == rd["a"].get_single_value_all()
    assert "bravo" == rd["b"].get_single_value_all()
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
    assert "alpha" == rd1["a"].get_single_value_all()
    rd1["a"] = "Foo"
    assert "Foo" == rd1["a"].get_single_value_all()


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
    assert rd1["a"] == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_set_list():
    rd1 = RangeDictionary(10, defaults)
    rl = RangedList(10, "gamma")
    rd1["g"] = rl
    new_dict = {"a": "alpha", "b": "bravo", "g": "gamma"}
    assert new_dict == rd1.get_value()


def test_empty():
    rd1 = RangeDictionary(10)
    rl = RangedList(10, "gamma")
    rd1["g"] = rl
    rd1["a"] = "alpha"
    rd1["b"] = ["bravo", "bravo", "bravo", "bravo", "bravo", "bravo", "bravo",
                "bravo", "bravo", "bravo"]
    new_dict = {"a": "alpha", "b": "bravo", "g": "gamma"}
    assert new_dict == rd1.get_value()


def test_iter_tests():
    rd1 = RangeDictionary(10)
    rl = RangedList(10, "gamma")
    rd1["g"] = rl
    rd1["a"] = "alpha"
    rd1["b"] = ["bravo", "bravo", "bravo", "bravo", "bravo", "bravo", "bravo",
                "bravo", "bravo", "bravo"]
    result = set(rd1.iteritems())
    check = {('a', 'alpha'), ('b', 'bravo'), ('g', 'gamma')}
    assert check == result
    result = set(rd1.itervalues())
    check = {'alpha', 'bravo', 'gamma'}
    assert check == result
    view = rd1[2]


def test_contains():
    rd1 = RangeDictionary(10)
    rl = RangedList(10, "gamma")
    rd1["g"] = rl
    rd1["a"] = "alpha"
    rd1["b"] = ["bravo", "bravo", "bravo", "bravo", "bravo", "bravo", "bravo",
                "bravo", "bravo", "bravo"]
    assert "a" in rd1
    assert "alpha" not in rd1
    assert 1 in rd1
    assert 14 not in rd1
    with pytest.raises(KeyError):
        assert (rl in rd1)


def test_reset():
    rd1 = RangeDictionary(10)
    rl = RangedList(10, "gamma")
    rd1["g"] = rl
    rd1["a"] = "alpha"
    rd1["b"] = ["bravo", "bravo", "bravo", "bravo", "bravo", "bravo", "bravo",
                "bravo", "bravo", "bravo"]
    rd1["a"] = "beta"
    rd1.reset("a")
    assert rd1["a"] == ["alpha", "alpha", "alpha", "alpha", "alpha", "alpha",
                        "alpha", "alpha", "alpha", "alpha"]


def test_bad_set():
    rd1 = RangeDictionary(10)
    with pytest.raises(KeyError):
        rd1[2] = "This should not work"
    with pytest.raises(KeyError):
        rd1[rd] = "This should not work"


def test_iter_by_slice():
    rd1 = RangeDictionary(10)
    rl = RangedList(10, "gamma")
    rd1["g"] = rl
    rd1["a"] = "alpha"
    rd1["b"] = ["bravo0", "bravo1", "bravo2", "bravo3", "bravo4", "bravo5",
                "bravo6", "bravo7", "bravo8+", "bravo9"]

    iterator = rd1.iter_values_by_slice(2, 4)
    assert {"a": "alpha", "b": "bravo2", "g": "gamma"} == next(iterator)
    assert {"a": "alpha", "b": "bravo3", "g": "gamma"} == next(iterator)
    with pytest.raises(StopIteration):
        next(iterator)

    iterator = rd1.iter_values_by_slice(2, 4, update_save=True)
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

    iterator = rd1.iter_values_by_slice(2, 4, key="b", update_save=True)
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
        2, 4, key=["b", "a"], update_save=True)
    assert {"a": "alpha", "b": "bravo2"} == next(iterator)
    rd1["b"][3] = "new3"
    assert {"a": "alpha", "b": "new3"} == next(iterator)
    with pytest.raises(StopIteration):
        next(iterator)
    rd1["b"][3] = "bravo3"


def test_defaults():
    assert "alpha" == rd.get_default("a")
    rd.set_default("a", "newa")
    assert "newa" == rd.get_default("a")


def test_bad_factory():
    with pytest.raises(KeyError):
        rd.view_factory([1, "a"])
