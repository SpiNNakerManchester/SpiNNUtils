# Copyright (c) 2017-2022 The University of Manchester
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

import logging
import pytest
from spinn_utilities.log import FormatAdapter
from testfixtures import LogCapture
from spinn_utilities.testing import log_checker

logger = FormatAdapter(logging.getLogger(__name__))


def test_log_checker():
    with LogCapture() as lc:
        logger.warning("This is a warning")
        logger.error("This is an error")
        log_checker.assert_logs_warning_contains(
            lc.records, "This is a warning")
        with pytest.raises(AssertionError):
            log_checker.assert_logs_warning_contains(
                lc.records, "never logged")
        log_checker. assert_logs_error_not_contains(
            lc.records, "This is a warning")
        with pytest.raises(AssertionError):
            log_checker. assert_logs_error_not_contains(
                lc.records, "This is an error")
