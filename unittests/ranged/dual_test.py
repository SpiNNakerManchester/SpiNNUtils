from spinn_utilities.ranged.ranged_list import RangedList


def test_simple():
    numerator = RangedList(5, 10, "ten")
    divisor = RangedList(5, 5, "five")
    div = numerator / divisor
    assert list(div) == [2, 2, 2, 2, 2]


def test_muliple():
    numerator = RangedList(5, 12.0, "numerator")
    divisor = RangedList(5, 4, "divisor")
    div = numerator / divisor
    assert list(div) == [3, 3, 3, 3, 3]
    divisor[1] = 6
    divisor[2] = 3
    divisor[3] = 8
    assert list(div) == [3, 2, 4, 1.5, 3]


def test_complex():
    numerator = RangedList(5, 12.0, "numerator")
    divisor = RangedList(5, 4, "divisor")
    div = numerator / divisor
    assert list(div) == [3, 3, 3, 3, 3]
    divisor[1:3] = 6
    numerator[2, 4] = 24
    assert list(div) == [3, 2, 4, 3, 6]


def test_get_value():
    numerator = RangedList(5, 12.0, "numerator")
    divisor = RangedList(5, 4, "divisor")
    div = numerator / divisor
    divisor[1:3] = 6
    numerator[2, 4] = 24
    assert div[2] == 4


def test_get_slice():
    numerator = RangedList(5, 12.0, "numerator")
    divisor = RangedList(5, 4, "divisor")
    div = numerator / divisor
    divisor[1:3] = 6
    numerator[2, 4] = 24
    assert div[2:4] == [4, 3]


def test_ranges():
    numerator = RangedList(10, 12.0, "numerator")
    divisor = RangedList(10, 4, "divisor")
    div = numerator / divisor
    divisor[1:6] = 6
    numerator[4:8] = 24
    assert [(0, 1, 3.0), (1, 4, 2.0), (4, 6, 4), (6, 8, 6), (8, 10, 3.0)] == \
        list(div.iter_ranges())


def test_ranges_by_slice():
    numerator = RangedList(10, 12.0, "numerator")
    divisor = RangedList(10, 4, "divisor")
    div = numerator / divisor
    divisor[1:6] = 6
    numerator[4:8] = 24
    assert [(2, 4, 2.0), (4, 6, 4), (6, 7, 6)] == \
        list(div.iter_ranges_by_slice(2, 7))


def test_get_ids():
    numerator = RangedList(5, 12.0, "numerator")
    divisor = RangedList(5, 4, "divisor")
    div = numerator / divisor
    divisor[1:3] = 6
    numerator[2, 4] = 24
    assert div[1:5:2] == [2, 3]
