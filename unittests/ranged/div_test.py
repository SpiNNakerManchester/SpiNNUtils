from spinn_utilities.ranged.ranged_list import RangedList
from spinn_utilities.ranged.div_view import DivList


def test_simple():
    numerator = RangedList(5, 10, "ten")
    divisor = RangedList(5, 5, "five")
    div = DivList(numerator, divisor, "div")
    assert list(div) == [2, 2, 2, 2, 2]


def test_muliple():
    numerator = RangedList(5, 12.0, "numerator")
    divisor = RangedList(5, 4, "divisor")
    div = DivList(numerator, divisor, "div")
    assert list(div) == [3, 3, 3, 3, 3]
    divisor[1] = 6
    divisor[2] = 3
    divisor[3] = 8
    assert list(div) == [3, 2, 4, 1.5, 3]


def test_complex():
    numerator = RangedList(5, 12.0, "numerator")
    divisor = RangedList(5, 4, "divisor")
    div = DivList(numerator, divisor, "div")
    assert list(div) == [3, 3, 3, 3, 3]
    divisor[1:3] = 6
    numerator[2, 4] = 24
    assert list(div) == [3, 2, 4, 3, 6]

