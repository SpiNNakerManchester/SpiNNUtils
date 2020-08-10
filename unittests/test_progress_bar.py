# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pytest
from testfixtures import LogCapture
from spinn_utilities.progress_bar import (
    ProgressBar, DummyProgressBar, _EnhancedProgressBar as
    EPB)
from spinn_utilities.testing import log_checker
from spinn_utilities import logger_utils
EPB._ENABLED = False


@pytest.mark.parametrize("pbclass", [ProgressBar, DummyProgressBar, EPB])
def test_operation(pbclass):
    p = pbclass(2, "abc")
    p.update()
    p.update()
    p.end()


@pytest.mark.parametrize("pbclass", [ProgressBar, DummyProgressBar, EPB])
def test_two_end(pbclass):
    p = pbclass(2, "abc2")
    p.update()
    p.update()
    p.end()
    p.end()


@pytest.mark.parametrize("pbclass", [ProgressBar, DummyProgressBar, EPB])
def test_with_operation(pbclass):
    with pbclass(2, "with_p") as p:
        p.update()
        p.update()


@pytest.mark.parametrize("pbclass", [ProgressBar, DummyProgressBar, EPB])
def test_check_length_full(pbclass):
    logger_utils.reset()
    p = pbclass(2, None)
    with LogCapture() as lc:
        p.update(3)
        log_checker.assert_logs_contains_once(
            "ERROR", lc.records, ProgressBar.TOO_MANY_ERROR)
    p.end()


@pytest.mark.parametrize("pbclass", [ProgressBar, DummyProgressBar, EPB])
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


@pytest.mark.parametrize("pbclass", [ProgressBar, DummyProgressBar, EPB])
def test_iteration_style(pbclass):
    coll = range(5)
    p = pbclass(coll, None)
    total = 0
    for value in p.over(coll):
        total += value
    assert total == 10
    assert p._number_of_things == 5


@pytest.mark.parametrize("pbclass", [ProgressBar, DummyProgressBar])
def test_set_completed(pbclass):
    logger_utils.reset()
    with LogCapture() as lc:
        p = pbclass(5, "Test set_completed")
        p.set_completed(2)
        p.set_completed(4)
        p.set_completed(3)
        p.set_completed(5)
        p.set_completed(3)
        p.end()
        p.end()
        log_checker._assert_logs_not_contains(
            "ERROR", lc.records, ProgressBar.TOO_MANY_ERROR)

@pytest.mark.parametrize("pbmagic", [False, True])
def test_bacon_enhancement(pbmagic):
    try:
        EPB._ENABLED = pbmagic
        seq = (1, 2, 3)
        assert sum(ProgressBar(seq, "foo").over(seq)) == 6
    finally:
        EPB._ENABLED = False
