from spinn_utilities.timer import Timer
from time import sleep


def test_create():
    t = Timer()
    assert t is not None


def test_basic_use():
    t = Timer()
    # Just check that these things don't throw
    t.start_timing()
    assert t.take_sample() is not None
    assert t.take_sample().total_seconds() > 0


def test_advanced_use():
    t = Timer()
    with t:
        sleep(0.1)
    assert t.measured_interval is not None
    assert t.measured_interval.total_seconds() >= 0.1
