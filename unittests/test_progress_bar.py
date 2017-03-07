import pytest
from spinn_utilities.progress_bar import ProgressBar


def test_operation():
    p = ProgressBar(2, "abc")
    p.update()
    p.update()
    p.end()


def test_check_length_full():
    p = ProgressBar(2, None)
    with pytest.raises(Exception):  # @UndefinedVariable
        p.update(3)
    p.end()


def test_check_length_addition():
    p = ProgressBar(2, None)
    p.update()
    p.update()
    with pytest.raises(Exception):  # @UndefinedVariable
        p.update()
    p.end()


def test_iteration_style():
    coll = range(5)
    p = ProgressBar(coll, None)
    total = 0
    for value in p.over(coll):
        total += value
    assert total == 10
    assert p._number_of_things == 5
