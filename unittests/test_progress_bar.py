import pytest
from spinn_utilities.progress_bar import ProgressBar, DummyProgressBar


@pytest.mark.parametrize("pbclass", [ProgressBar, DummyProgressBar])
def test_operation(pbclass):
    p = pbclass(2, "abc")
    p.update()
    p.update()
    p.end()


@pytest.mark.parametrize("pbclass", [ProgressBar, DummyProgressBar])
def test_two_end(pbclass):
    p = pbclass(2, "abc2")
    p.update()
    p.update()
    p.end()
    p.end()


@pytest.mark.parametrize("pbclass", [ProgressBar, DummyProgressBar])
def test_with_operation(pbclass):
    with pbclass(2, "with_p") as p:
        p.update()
        p.update()


@pytest.mark.parametrize("pbclass", [ProgressBar, DummyProgressBar])
def test_check_length_full(pbclass):
    p = pbclass(2, None)
    with pytest.raises(Exception):
        p.update(3)
    p.end()


@pytest.mark.parametrize("pbclass", [ProgressBar, DummyProgressBar])
def test_check_length_addition(pbclass):
    p = pbclass(2, None)
    p.update()
    p.update()
    with pytest.raises(Exception):
        p.update()
    p.end()


@pytest.mark.parametrize("pbclass", [ProgressBar, DummyProgressBar])
def test_iteration_style(pbclass):
    coll = range(5)
    p = pbclass(coll, None)
    total = 0
    for value in p.over(coll):
        total += value
    assert total == 10
    assert p._number_of_things == 5
