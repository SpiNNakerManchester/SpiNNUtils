from spinn_utilities.ranged.ranged_list import RangedList


def test_simple():
    rl = RangedList(10, "a")
    ranges = rl.get_ranges()
    assert list(rl) == ["a", "a", "a", "a", "a", "a", "a", "a", "a", "a"]
    assert len(ranges) == 1
    assert ranges[0][0] == 0
    assert ranges[0][1] == 10
    assert ranges[0][2] == "a"
    assert rl[3] == "a"


def test_insert_id():
    rl = RangedList(10, "a")
    rl[4] = "b"
    assert "b" == rl[4]
    assert "a" == rl[3]
    ranges = rl.get_ranges()
    assert list(rl) == ["a", "a", "a", "a", "b", "a", "a", "a", "a", "a"]
    assert ranges == [(0, 4, "a"), (4, 5, "b"), (5, 10, "a")]
    rl[5] = "b"
    assert list(rl) == ["a", "a", "a", "a", "b", "b", "a", "a", "a", "a"]
    ranges = rl.get_ranges()
    assert ranges == [(0, 4, "a"), (4, 6, "b"), (6, 10, "a")]


def test_insert_slice_part_range():
    rl = RangedList(10, "a")
    assert not "b" in rl
    rl[4:6] = "b"
    assert "b" in rl
    ranges = rl.get_ranges()
    assert list(rl) == ["a", "a", "a", "a", "b", "b", "a", "a", "a", "a"]
    assert ranges == [(0, 4, "a"), (4, 6, "b"), (6, 10, "a")]
    assert "a" in rl
    assert not "c" in rl


def test_insert_slice_up_to():
    rl = RangedList(10, "a")
    rl[3:7] = "b"
    assert rl.get_ranges() == [(0, 3, "a"), (3, 7, "b"), (7, 10, "a")]
    rl[1:3] = "c"
    assert list(rl) == ["a", "c", "c", "b", "b", "b", "b", "a", "a", "a"]
    assert rl.get_ranges() == [(0, 1, "a"), (1, 3, "c"), (3, 7, "b"), (7, 10, "a")]


def test_insert_slice_start_over_lap_to():
    rl = RangedList(10, "a")
    rl[3:7] = "b"
    assert rl.get_ranges() == [(0, 3, "a"), (3, 7, "b"), (7, 10, "a")]
    rl[1:5] = "c"
    assert list(rl) == ["a", "c", "c", "c", "c", "b", "b", "a", "a", "a"]
    assert rl.get_ranges() == [(0, 1, "a"), (1, 5, "c"), (5, 7, "b"), (7, 10, "a")]


def test_insert_slice_start_over_lap_both():
    rl = RangedList(10, "a")
    rl[3:7] = "b"
    assert rl.get_ranges() == [(0, 3, "a"), (3, 7, "b"), (7, 10, "a")]
    rl[1:8] = "c"
    assert list(rl) == ["a", "c", "c", "c", "c", "c", "c", "c", "a", "a"]
    assert rl.get_ranges() == [(0, 1, "a"), (1, 8, "c"), (8, 10, "a")]


def test_insert_slice_to_previous():
    rl = RangedList(10, "a")
    rl[3:7] = "b"
    assert rl.get_ranges() == [(0, 3, "a"), (3, 7, "b"), (7, 10, "a")]
    rl[2:5] = "a"
    assert list(rl) == ["a", "a", "a", "a", "a", "b", "b", "a", "a", "a"]
    assert rl.get_ranges() == [(0, 5, "a"), (5, 7, "b"), (7, 10, "a")]


def test_insert_end():
    rl = RangedList(10, "a")
    rl[1] = "b"
    assert rl.get_ranges() == [(0, 1, "a"), (1, 2, "b"), (2, 10, "a")]
    rl[4:6] = "c"
    r = rl.get_ranges()
    assert rl.get_ranges() == [(0, 1, "a"), (1, 2, "b"), (2, 4, "a"), (4, 6, "c"),
                               (6, 10, "a")]


def test_insert_list():
    rl = RangedList(10, "a")
    rl[4, 8, 2] = "b"
    assert list(rl) == ["a", "a", "b", "a", "b", "a", "a", "a", "b", "a"]
    assert rl.get_ranges() == [(0, 2, "a"), (2, 3, "b"), (3, 4, "a"), (4, 5, "b"),
                               (5, 8, "a"), (8, 9, "b"), (9, 10, "a")]
    rl[3] = "b"
    assert list(rl) == ["a", "a", "b", "b", "b", "a", "a", "a", "b", "a"]
    assert rl.get_ranges() == [(0, 2, "a"), (2, 5, "b"), (5, 8, "a"), (8, 9, "b"),
                               (9, 10, "a")]
    rl[3] = "x"
    assert list(rl) == ["a", "a", "b", "x", "b", "a", "a", "a", "b", "a"]
    assert rl.get_ranges() == [(0, 2, "a"), (2, 3, "b"), (3, 4, "x"), (4, 5, "b"),
                               (5, 8, "a"), (8, 9, "b"), (9, 10, "a")]
    assert rl.count("b") == 3


def test_iter_simple():
    rl = RangedList(10, "a")
    for i in range(10):
        rl[i] = i
    assert list(rl) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_iter_complex():
    rl = RangedList(size=10, default="a", key="alpha")
    list_iter = rl.iter()
    assert "a" == list_iter.next()  # 0
    assert "a" == list_iter.next()  # 1
    assert "a" == list_iter.next()  # 2
    rl[1] = "b"
    assert "a" == list_iter.next()  # 3
    rl[4:6] = "c"
    assert "c" == list_iter.next()  # 4
    assert "c" == list_iter.next()  # 5
    assert "a" == list_iter.next()  # 6

def test_iter():
    rl = RangedList(size=10, default="a", key="alpha")
    it = rl.iter()
    assert list(it) == ["a", "a", "a", "a", "a", "a", "a", "a", "a", "a"]

def test_ranges_by_id():
    rl = RangedList(size=10, default="a", key="alpha")
    assert [(3, 4, "a")] == list(rl.iter_ranges_by_id(3))

def test_ranges_by_slice():
    rl = RangedList(size=10, default="a", key="alpha")
    assert [(3, 8, "a")] == list(rl.iter_ranges_by_slice(3, 8))
    rl[5] = "foo"
    assert [(3, 5, "a"), (5, 6, "foo"), (6, 8, "a")] == \
           list(rl.iter_ranges_by_slice(3, 8))

def test_ranges_by_ids():
    rl = RangedList(size=10, default="a", key="alpha")
    assert [(1, 4, "a"), (7, 8, "a"), (4, 5, "a")] == \
           list(rl.iter_ranges_by_ids((1, 2, 3, 7, 4)))
    rl[6] = "foo"
    assert [(1, 4, "a"), (7, 8, "a"), (4, 5, "foo")] == \
           list(rl.iter_ranges_by_ids((1, 2, 3, 7, 4)))
    rl[3] = "foo"
    assert [(1, 3, "a"), (3, 4, "foo"), (7, 8, "a"), (4, 5, "a")] == \
           list(rl.iter_ranges_by_ids((1, 2, 3, 7, 4)))
