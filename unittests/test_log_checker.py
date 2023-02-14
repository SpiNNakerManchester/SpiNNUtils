# Copyright (c) 2017 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
