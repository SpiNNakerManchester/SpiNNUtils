from spinn_utilities.ranged.ranged_list import RangedList


def test_simple():
    rl = RangedList(5, [0, 1, 2, 3, 4])
    ranges = rl.get_ranges()
    assert rl == [0, 1, 2, 3, 4]
    assert len(ranges) == 5
    assert ranges == [(0, 1, 0), (1, 2, 1), (2, 3, 2), (3, 4, 3), (4, 5, 4)]
    assert rl[3] == 3


def test_insert_slice_part_range():
    rl = RangedList(5, [0, 1, 2, 3, 4])
    assert 8 not in rl
    rl[1:3] = 8
    assert 8 in rl
    ranges = rl.get_ranges()
    assert rl == [0, 8, 8, 3, 4]
    assert ranges == [(0, 1, 0), (1, 3, 8), (3, 4, 3), (4, 5, 4)]
    assert 8 in rl
    assert 9 not in rl
    assert [8, 3] == rl[2:4]


def test_insert_complex_slice():
    rl = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    assert rl[4:8:2] == [4, 6]
    assert "b" not in rl
    rl[4:8:2] = "b"
    assert "b" in rl
    assert rl == [0, 1, 2, 3, "b", 5, "b", 7, 8, 9]
    ranges = rl.get_ranges()
    assert ranges == [(0, 1, 0), (1, 2, 1), (2, 3, 2), (3, 4, 3),
                      (4, 5, "b"), (5, 6, 5), (6, 7, "b"), (7, 8, 7),
                      (8, 9, 8), (9, 10, 9)]
    assert 2 in rl
    assert "c" not in rl
    assert [3, "b"] == rl[3:7:3]


def test_insert_slice_up_to():
    rl = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    rl[3:7] = "b"
    assert rl.get_ranges() == [(0, 1, 0), (1, 2, 1), (2, 3, 2), (3, 7, "b"),
                               (7, 8, 7), (8, 9, 8), (9, 10, 9)]

    rl[1:3] = "c"
    assert rl == [0, "c", "c", "b", "b", "b", "b", 7, 8, 9]
    assert rl.get_ranges() == [(0, 1, 0), (1, 3, "c"), (3, 7, "b"),
                               (7, 8, 7), (8, 9, 8), (9, 10, 9)]


def test_insert_slice_start_over_lap_to():
    rl = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    rl[3:7] = "b"
    rl[1:5] = "c"
    assert rl == [0, "c", "c", "c", "c", "b", "b", 7, 8, 9]
    assert rl.get_ranges() == [(0, 1, 0), (1, 5, "c"), (5, 7, "b"),
                               (7, 8, 7), (8, 9, 8), (9, 10, 9)]


def test_insert_slice_start_over_lap_both():
    rl = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    rl[3:7] = "b"
    rl[1:8] = "c"
    assert rl == [0, "c", "c", "c", "c", "c", "c", "c", 8, 9]
    assert rl.get_ranges() == [(0, 1, 0), (1, 8, "c"), (8, 9, 8),
                               (9, 10, 9)]


def test_insert_list():
    rl = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    rl[4, 8, 2] = "b"
    assert rl == [0, 1, "b", 3, "b", 5, 6, 7, "b", 9]
    assert rl.get_ranges() == [(0, 1, 0), (1, 2, 1), (2, 3, "b"), (3, 4, 3),
                               (4, 5, "b"), (5, 6, 5), (6, 7, 6), (7, 8, 7),
                               (8, 9, "b"), (9, 10, 9)]
    rl[3] = "b"
    assert rl == [0, 1, "b", "b", "b", 5, 6, 7, "b", 9]
    assert rl.get_ranges() == [(0, 1, 0), (1, 2, 1), (2, 5, "b"), (5, 6, 5),
                               (6, 7, 6), (7, 8, 7), (8, 9, "b"), (9, 10, 9)]
    rl[3] = "x"
    assert rl == [0, 1, "b", "x", "b", 5, 6, 7, "b", 9]
    assert rl.get_ranges() == [(0, 1, 0), (1, 2, 1), (2, 3, "b"), (3, 4, "x"),
                               (4, 5, "b"), (5, 6, 5), (6, 7, 6), (7, 8, 7),
                               (8, 9, "b"), (9, 10, 9)]
    assert rl.count("b") == 3


def test_iter_simple():
    rl = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    for i in range(10):
        rl[i] = i
    assert rl == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_iter_complex():
    rl = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    list_iter = rl.iter()
    assert 0 == next(list_iter)  # 0
    assert 1 == next(list_iter)  # 1
    assert 2 == next(list_iter)  # 2
    rl[1] = "b"
    assert 3 == next(list_iter)  # 3
    rl[4:6] = "c"
    assert "c" == next(list_iter)  # 4
    assert "c" == next(list_iter)  # 5
    assert 6 == next(list_iter)  # 6


def test_iter():
    rl = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    it = rl.iter()
    assert list(it) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_ranges_by_id():
    rl = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    assert [(3, 4, 3)] == list(rl.iter_ranges_by_id(3))


def test_ranges_by_slice():
    rl = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    assert [(3, 4, 3), (4, 5, 4), (5, 6, 5), (6, 7, 6), (7, 8, 7)] == \
        list(rl.iter_ranges_by_slice(3, 8))
    rl[5] = "foo"
    assert [(3, 4, 3), (4, 5, 4), (5, 6, "foo"), (6, 7, 6), (7, 8, 7)] == \
        list(rl.iter_ranges_by_slice(3, 8))


def test_ranges_by_ids():
    rl = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    assert [(1, 2, 1), (2, 3, 2), (3, 4, 3), (7, 8, 7), (4, 5, 4)] == \
        list(rl.iter_ranges_by_ids((1, 2, 3, 7, 4)))
    rl[6] = "foo"
    assert [(1, 2, 1), (2, 3, 2), (3, 4, 3), (7, 8, 7), (4, 5, 4)] == \
        list(rl.iter_ranges_by_ids((1, 2, 3, 7, 4)))
    rl[3] = "foo"
    assert [(1, 2, 1), (2, 3, 2), (3, 4, "foo"), (7, 8, 7), (4, 5, 4)] == \
        list(rl.iter_ranges_by_ids((1, 2, 3, 7, 4)))


def test_iter_by_slice():
    rl = RangedList(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    assert [2, 3, 4] == list(rl.iter_by_slice(2, 5))
    rl[3:7] = "b"
    assert [2, "b", "b"] == list(rl.iter_by_slice(2, 5))
