from spinn_utilities.log import FormatAdapter
import logging


class MockLog(object):

    def __init__(self):
        self.last_level = None
        self.last_msg = None
        self.last_args = None
        self.last_kwargs = None

    def isEnabledFor(self, level):
        return level == logging.INFO

    def _log(self, level, msg, *args, **kwargs):
        self.last_level = level
        self.last_msg = msg
        self.last_args = args
        self.last_kwargs = kwargs


def test_logger_adapter():
    log = MockLog()
    logger = FormatAdapter(log)
    logger.debug("Debug {}", "debug")
    assert log.last_level is None
    logger.info("Info {}", "info")
    assert log.last_level == logging.INFO
    assert str(log.last_msg) == "Info info"
    logger.info("Test %s", "test")
    assert str(log.last_msg) == "Test %s"
