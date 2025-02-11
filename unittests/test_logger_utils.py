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

import logging
from testfixtures import LogCapture  # type: ignore[import]
import unittest
from spinn_utilities import logger_utils
from spinn_utilities.log import FormatAdapter
from spinn_utilities.testing import log_checker

logging.basicConfig()
logger = FormatAdapter(logging.getLogger(__name__))


class TestLoggerUtils(unittest.TestCase):

    def tearDown(self) -> None:
        logger_utils.reset()

    def test_one(self) -> None:
        with LogCapture() as lc:
            logger_utils.warn_once(logger, "a log warning")
            log_checker.assert_logs_contains_once("WARNING", lc.records,
                                                  "a log warning")

    def test_two(self) -> None:
        with LogCapture() as lc:
            logger_utils.warn_once(logger, "a log warning")
            logger_utils.warn_once(logger, "another log warning")
            log_checker.assert_logs_contains_once("WARNING", lc.records,
                                                  "a log warning")
            log_checker.assert_logs_contains_once("WARNING", lc.records,
                                                  "another log warning")

    def test_twice(self) -> None:
        with LogCapture() as lc:
            logger_utils.warn_once(logger, "a log warning")
            logger_utils.warn_once(logger, "a log warning")
            log_checker.assert_logs_contains_once("WARNING", lc.records,
                                                  "a log warning")

    def test_multiple(self) -> None:
        with LogCapture() as lc:
            logger_utils.warn_once(logger, "a log warning")
            logger_utils.warn_once(logger, "another log warning")
            logger_utils.warn_once(logger, "a log warning")
            log_checker.assert_logs_contains_once("WARNING", lc.records,
                                                  "a log warning")

    def test_error(self) -> None:
        with LogCapture() as lc:
            logger_utils.error_once(logger, "a log Error")
            logger_utils.warn_once(logger, "another log error")
            logger_utils.warn_once(logger, "a log warning")
            logger_utils.error_once(logger, "a log Error")
            log_checker.assert_logs_contains_once(
                "ERROR", lc.records, "a log Error")
            log_checker.assert_logs_error_not_contains(
                lc.records, "another log error")
