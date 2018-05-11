from spinn_utilities.ranged import RangeDictionary

defaults = {"a": "alpha", "b": "bravo"}
rd = RangeDictionary(10, defaults)


def test_full():
    assert [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] == list(rd.ids())


def test_single():
    view = rd[2]
    assert [2] == list(view.ids())


def test_simple_slice():
    view = rd[2:6]
    assert [2, 3, 4, 5] == list(view.ids())


def test_extended_slice():
    view = rd[2:8:2]
    assert [2, 4, 6] == list(view.ids())


def test_tuple():
    view = rd[2, 4, 7]
    assert [2, 4, 7] == list(view.ids())


def test_unsorted_tuple():
    view = rd[2, 7, 3]
    assert [2, 7, 3] == list(view.ids())


def test_list():
    ids = [2, 3, 7]
    view = rd[ids]
    assert [2, 3, 7] == list(view.ids())


def test_double_slice():
    view1 = rd[2:7]
    assert [2, 3, 4, 5, 6] == list(view1.ids())
    view2 = view1[2:4]
    assert [4, 5] == list(view2.ids())


def test_double_list():
    ids = [2, 7, 1, 3, 5, 8]
    view1 = rd[ids]
    assert [2, 7, 1, 3, 5, 8] == list(view1.ids())
    view2 = view1[2, 3, 5]
    assert [1, 3, 8] == list(view2.ids())
