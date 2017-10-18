from spinn_utilities.lazy.ranged_list import RangedList


def test_simple():
    rl = RangedList(10, "a")
    ranges = rl.ranges()
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
    ranges = rl.ranges()
    assert list(rl) == ["a", "a", "a", "a", "b", "a", "a", "a", "a", "a"]
    assert ranges == [(0, 4, "a"), (4, 5, "b"), (5, 10, "a")]
    rl[5] = "b"
    assert list(rl) == ["a", "a", "a", "a", "b", "b", "a", "a", "a", "a"]
    ranges = rl.ranges()
    assert ranges == [(0, 4, "a"), (4, 6, "b"), (6, 10, "a")]


def test_insert_slice_part_range():
    rl = RangedList(10, "a")
    assert not "b" in rl
    rl[4:6] = "b"
    assert "b" in rl
    ranges = rl.ranges()
    assert list(rl) == ["a", "a", "a", "a", "b", "b", "a", "a", "a", "a"]
    assert ranges == [(0, 4, "a"), (4, 6, "b"), (6, 10, "a")]
    assert "a" in rl
    assert not "c" in rl


def test_insert_slice_up_to():
    rl = RangedList(10, "a")
    rl[3:7] = "b"
    assert rl.ranges() == [(0, 3, "a"), (3, 7, "b"), (7, 10, "a")]
    rl[1:3] = "c"
    assert list(rl) == ["a", "c", "c", "b", "b", "b", "b", "a", "a", "a"]
    assert rl.ranges() == [(0, 1, "a"), (1, 3, "c"), (3, 7, "b"), (7, 10, "a")]


def test_insert_slice_start_over_lap_to():
    rl = RangedList(10, "a")
    rl[3:7] = "b"
    assert rl.ranges() == [(0, 3, "a"), (3, 7, "b"), (7, 10, "a")]
    rl[1:5] = "c"
    assert list(rl) == ["a", "c", "c", "c", "c", "b", "b", "a", "a", "a"]
    assert rl.ranges() == [(0, 1, "a"), (1, 5, "c"), (5, 7, "b"), (7, 10, "a")]


def test_insert_slice_start_over_lap_both():
    rl = RangedList(10, "a")
    rl[3:7] = "b"
    assert rl.ranges() == [(0, 3, "a"), (3, 7, "b"), (7, 10, "a")]
    rl[1:8] = "c"
    assert list(rl) == ["a", "c", "c", "c", "c", "c", "c", "c", "a", "a"]
    assert rl.ranges() == [(0, 1, "a"), (1, 8, "c"), (8, 10, "a")]


def test_insert_slice_to_previous():
    rl = RangedList(10, "a")
    rl[3:7] = "b"
    assert rl.ranges() == [(0, 3, "a"), (3, 7, "b"), (7, 10, "a")]
    rl[2:5] = "a"
    assert list(rl) == ["a", "a", "a", "a", "a", "b", "b", "a", "a", "a"]
    assert rl.ranges() == [(0, 5, "a"), (5, 7, "b"), (7, 10, "a")]


def test_insert_end():
    rl = RangedList(10, "a")
    rl[1] = "b"
    assert rl.ranges() == [(0, 1, "a"), (1, 2, "b"), (2, 10, "a")]
    rl[4:6] = "c"
    r = rl.ranges()
    assert rl.ranges() == [(0, 1, "a"), (1, 2, "b"), (2, 4, "a"), (4, 6, "c"),
                           (6, 10, "a")]


def test_insert_list():
    rl = RangedList(10, "a")
    rl[4, 8, 2] = "b"
    assert list(rl) == ["a", "a", "b", "a", "b", "a", "a", "a", "b", "a"]
    assert rl.ranges() == [(0, 2, "a"), (2, 3, "b"), (3, 4, "a"), (4, 5, "b"),
                           (5, 8, "a"), (8, 9, "b"), (9, 10, "a")]
    rl[3] = "b"
    assert list(rl) == ["a", "a", "b", "b", "b", "a", "a", "a", "b", "a"]
    assert rl.ranges() == [(0, 2, "a"), (2, 5, "b"), (5, 8, "a"), (8, 9, "b"),
                           (9, 10, "a")]
    rl[3] = "x"
    assert list(rl) == ["a", "a", "b", "x", "b", "a", "a", "a", "b", "a"]
    assert rl.ranges() == [(0, 2, "a"), (2, 3, "b"), (3, 4, "x"), (4, 5, "b"),
                           (5, 8, "a"), (8, 9, "b"), (9, 10, "a")]
    assert rl.count("b") == 3


def test_iter_simple():
    rl = RangedList(10, "a")
    for i in range(10):
        rl[i] = i
    assert list(rl) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_iter_complex():
    rl = RangedList(size=10, default="a", key="alpha")
    list_iter = iter(rl)
    assert "a" == list_iter.next()  # 0
    assert "a" == list_iter.next()  # 1
    assert "a" == list_iter.next()  # 2
    rl[1] = "b"
    assert "a" == list_iter.next()  # 3
    rl[4:6] = "c"
    assert "c" == list_iter.next()  # 4
    assert "c" == list_iter.next()  # 5
    assert "a" == list_iter.next()  # 6

def test_fast_iter():
    rl = RangedList(size=10, default="a", key="alpha")
    it = rl.fastiter()
    print it
    for i in it:
        print i