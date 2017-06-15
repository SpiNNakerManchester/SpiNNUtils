from spinn_utilities import logger_utils
import spinn_utilities.testing.log_checker as log_checker
import logging
from testfixtures import LogCapture
import unittest

logging.basicConfig()
logger = logging.getLogger(__name__)


class TestLoggerUtils(unittest.TestCase):

    def tearDown(self):
        logger_utils.reset()

    def test_one(self):
        with LogCapture() as l:
            logger_utils.warn_once(logger, "a log warning")
            log_checker.assert_logs_contains_once("WARNING", l.records,
                                                  "a log warning")

    def test_two(self):
        with LogCapture() as l:
            logger_utils.warn_once(logger, "a log warning")
            logger_utils.warn_once(logger, "another log warning")
            log_checker.assert_logs_contains_once("WARNING", l.records,
                                                  "a log warning")
            log_checker.assert_logs_contains_once("WARNING", l.records,
                                                  "another log warning")

    def test_twice(self):
        with LogCapture() as l:
            logger_utils.warn_once(logger, "a log warning")
            logger_utils.warn_once(logger, "a log warning")
            log_checker.assert_logs_contains_once("WARNING", l.records,
                                                  "a log warning")

    def test_multiple(self):
        with LogCapture() as l:
            logger_utils.warn_once(logger, "a log warning")
            logger_utils.warn_once(logger, "another log warning")
            logger_utils.warn_once(logger, "a log warning")
            log_checker.assert_logs_contains_once("WARNING", l.records,
                                                  "a log warning")
