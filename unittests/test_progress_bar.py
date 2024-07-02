# Copyright (c) 2017 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from testfixtures import LogCapture  # type: ignore[import]
from spinn_utilities.config_setup import unittest_setup
from spinn_utilities.progress_bar import (
    ProgressBar, DummyProgressBar, _EnhancedProgressBar as
    EPB)
from spinn_utilities.testing import log_checker
from spinn_utilities import logger_utils

EPB._enabled = False


@pytest.mark.parametrize("pbclass", [ProgressBar, DummyProgressBar, EPB])
def test_operation(pbclass):
    unittest_setup()
    p = pbclass(2, "abc")
    p.update()
    p.update()
    p.end()


@pytest.mark.parametrize("pbclass", [ProgressBar, DummyProgressBar, EPB])
def test_two_end(pbclass):
    unittest_setup()
    p = pbclass(2, "abc2")
    p.update()
    p.update()
    p.end()
    p.end()


@pytest.mark.parametrize("pbclass", [ProgressBar, DummyProgressBar, EPB])
def test_with_operation(pbclass):
    unittest_setup()
    with pbclass(2, "with_p") as p:
        p.update()
        p.update()


@pytest.mark.parametrize("pbclass", [ProgressBar, DummyProgressBar, EPB])
def test_check_length_full(pbclass):
    unittest_setup()
    logger_utils.reset()
    p = pbclass(2, None)
    with LogCapture() as lc:
        p.update(3)
        log_checker.assert_logs_contains_once(
            "ERROR", lc.records, ProgressBar.TOO_MANY_ERROR)
    p.end()


@pytest.mark.parametrize("pbclass", [ProgressBar, DummyProgressBar, EPB])
def test_check_length_addition(pbclass):
    unittest_setup()
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
def test_repr(pbclass):
    p = pbclass(2, "repr test")
    assert "repr test" in repr(p)


@pytest.mark.parametrize("pbclass", [ProgressBar, DummyProgressBar, EPB])
def test_iteration_style(pbclass):
    unittest_setup()
    coll = range(5)
    p = pbclass(coll, None)
    total = 0
    for value in p.over(coll):
        total += value
    assert total == 10
    assert p._number_of_things == 5


@pytest.mark.parametrize("pbmagic", [False, True])
def test_bacon_enhancement(pbmagic):
    unittest_setup()
    try:
        EPB._enabled = pbmagic
        seq = (1, 2, 3)
        assert sum(ProgressBar(seq, "foo").over(seq)) == 6
    finally:
        EPB._enabled = False
