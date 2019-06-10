from spinn_utilities.find_max_success import (
    find_max_success,  search_for_max_success)


def test_0():
    result = find_max_success(12, lambda x: x < 0)
    assert result == 0


def test_1():
    result = find_max_success(12, lambda x: x <= 1)
    assert result == 1


def test_2():
    result = find_max_success(12, lambda x: x <= 2)
    assert result == 2


def test_3():
    result = find_max_success(12, lambda x: x <= 3)
    assert result == 3


def test_4():
    result = find_max_success(12, lambda x: x <= 4)
    assert result == 4


def test_5():
    result = find_max_success(12, lambda x: x <= 5)
    assert result == 5


def test_6():
    result = find_max_success(12, lambda x: x <= 6)
    assert result == 6


def test_7():
    result = find_max_success(12, lambda x: x <= 7)
    assert result == 7


def test_8():
    result = find_max_success(12, lambda x: x <= 8)
    assert result == 8


def test_9():
    result = find_max_success(12, lambda x: x <= 9)
    assert result == 9


def test_10():
    result = find_max_success(12, lambda x: x <= 10)
    assert result == 10


def test_11():
    result = find_max_success(12, lambda x: x <= 11)
    assert result == 11


def test_12():
    result = find_max_success(12, lambda x: x <= 12)
    assert result == 12


def test_17():
    result = find_max_success(12, lambda x: x <= 12)
    assert result == 12


def test_negative():
    result = search_for_max_success(-10, 12, lambda x: x <= -2)
    assert result == -2


def test_negative_2():
    result = search_for_max_success(-10, 12, lambda x: x <= 2)
    assert result == 2
