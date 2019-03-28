import pytest
from testfixtures import LogCapture
from spinn_utilities.progress_bar import ProgressBar, DummyProgressBar
from spinn_utilities.testing import log_checker
from spinn_utilities import logger_utils


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
    logger_utils.reset()
    p = pbclass(2, None)
    with LogCapture() as lc:
        p.update(3)
        log_checker.assert_logs_contains_once(
            "ERROR", lc.records, ProgressBar.TOO_MANY_ERROR)
    p.end()


@pytest.mark.parametrize("pbclass", [ProgressBar, DummyProgressBar])
def test_check_length_addition(pbclass):
    logger_utils.reset()
    p = pbclass(2, None)
    p.update()
    p.update()
    with LogCapture() as lc:
        p.update()
        log_checker.assert_logs_contains_once(
            "ERROR", lc.records, ProgressBar.TOO_MANY_ERROR)
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
