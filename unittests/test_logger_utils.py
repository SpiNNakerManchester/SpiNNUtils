import logging
from testfixtures import LogCapture
import unittest
from spinn_utilities import logger_utils
from spinn_utilities.testing import log_checker

logging.basicConfig()
logger = logging.getLogger(__name__)


class TestLoggerUtils(unittest.TestCase):

    def tearDown(self):
        logger_utils.reset()

    def test_one(self):
        with LogCapture() as lc:
            logger_utils.warn_once(logger, "a log warning")
            log_checker.assert_logs_contains_once("WARNING", lc.records,
                                                  "a log warning")

    def test_two(self):
        with LogCapture() as lc:
            logger_utils.warn_once(logger, "a log warning")
            logger_utils.warn_once(logger, "another log warning")
            log_checker.assert_logs_contains_once("WARNING", lc.records,
                                                  "a log warning")
            log_checker.assert_logs_contains_once("WARNING", lc.records,
                                                  "another log warning")

    def test_twice(self):
        with LogCapture() as lc:
            logger_utils.warn_once(logger, "a log warning")
            logger_utils.warn_once(logger, "a log warning")
            log_checker.assert_logs_contains_once("WARNING", lc.records,
                                                  "a log warning")

    def test_multiple(self):
        with LogCapture() as lc:
            logger_utils.warn_once(logger, "a log warning")
            logger_utils.warn_once(logger, "another log warning")
            logger_utils.warn_once(logger, "a log warning")
            log_checker.assert_logs_contains_once("WARNING", lc.records,
                                                  "a log warning")

    def test_error(self):
        with LogCapture() as lc:
            logger_utils.error_once(logger, "a log Error")
            logger_utils.warn_once(logger, "another log error")
            logger_utils.warn_once(logger, "a log warning")
            log_checker.assert_logs_contains_once(
                "ERROR", lc.records, "a log Error")
            log_checker.assert_logs_error_not_contains(
                lc.records, "another log error")
