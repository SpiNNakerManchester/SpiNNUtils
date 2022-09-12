# Copyright (c) 2017-2018 The University of Manchester
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
from spinn_utilities.log import (
    ConfiguredFilter, ConfiguredFormatter, FormatAdapter,
    LogLevelTooHighException)
from spinn_utilities.log_store import LogStore
from spinn_utilities.overrides import overrides


class MockLog(object):
    def __init__(self):
        self.last_level = None
        self.last_msg = None
        self.last_args = None
        self.last_kwargs = None

    def isEnabledFor(self, level):
        return level >= logging.INFO

    def _log(self, level, msg, *args, **kwargs):
        self.last_level = level
        self.last_msg = msg
        self.last_args = args
        self.last_kwargs = kwargs

    def getEffectiveLevel(self):
        return logging.INFO

    @property
    def manager(self):
        return self

    @property
    def disable(self):
        return logging.DEBUG


class MockLogStore(LogStore):

    def __init__(self):
        self.data = []

    @overrides(LogStore.store_log)
    def store_log(self, level, message, timestamp=None):
        if level == logging.CRITICAL:
            1/0
        self.data.append((level, message))

    @overrides(LogStore.retreive_log_messages)
    def retreive_log_messages(self, min_level=0):
        result = []
        for (level, message) in self.data:
            if level >= min_level:
                result.append((level, message))
        return result

    @overrides(LogStore.get_location)
    def get_location(self):
        return "MOCK"


def test_logger_adapter():
    log = MockLog()
    logger = FormatAdapter(log)
    logger._pop_not_logged_messages()  # clear the log
    logger.debug("Debug {}", "debug")
    assert log.last_level is None
    logger.info("Info {}", "info")
    assert log.last_level == logging.INFO
    assert str(log.last_msg) == "Info info"
    logger.info("Test %s", "test")
    assert str(log.last_msg) == "Test %s"
    logger.warning("boo")
    assert str(log.last_msg) == "boo"
    assert log.last_level == logging.WARN
    logger.error("foo")
    assert str(log.last_msg) == "foo"
    assert log.last_level == logging.ERROR
    logger.critical("bar")
    assert str(log.last_msg) == "bar"
    assert log.last_level == logging.CRITICAL
    logger.set_kill_level(logging.CRITICAL)
    try:
        logger.critical("This is too high")
        assert False
    except LogLevelTooHighException:
        pass
    logger.set_kill_level()
    logger.critical("Should be ok now")
    assert len(logger._pop_not_logged_messages())


def test_logger_dict():
    log = MockLog()
    logger = FormatAdapter(log)
    mydict = {1: "one", 2: "two"}
    logger.info(mydict)
    assert str(log.last_msg) == "{1: 'one', 2: 'two'}"


def test_logger_exception():
    log = MockLog()
    logger = FormatAdapter(log)
    logger._pop_not_logged_messages()  # clear the log

    class Exn(Exception):
        pass

    try:
        raise Exn("hi")
    except Exn as ex:
        e = ex
        logger.exception("ho")

    assert str(e) == "hi"
    assert str(log.last_msg) == "ho"
    assert "exc_info" in log.last_kwargs
    assert log.last_level == logging.ERROR
    assert len(logger._pop_not_logged_messages()) == 1


class MockConfig1(object):

    def get(self, section, option):
        return "debug"

    def has_section(self, section):
        return False


def test_weird_config1():
    ConfiguredFormatter(MockConfig1())
    ConfiguredFilter(MockConfig1())


class MockConfig2(object):

    def get(self, section, option):
        return "critical"

    def has_section(self, section):
        return True

    def has_option(self, section, option):
        return option == 'warning'


def test_weird_config2():
    ConfiguredFormatter(MockConfig2())
    ConfiguredFilter(MockConfig2())


def test_log_store():
    logger = FormatAdapter(MockLog())
    logger2 = FormatAdapter(MockLog())
    logger2.warning("This is early")
    logger2.info("Pre {}", "info")
    store = MockLogStore()
    logger2.set_log_store(store)
    assert 0 == len(FormatAdapter._pop_not_logged_messages())
    logger.warning("This is a warning")
    logger2.error("And an Error")
    logger.info("This is an {}", "info")
    info = store.retreive_log_messages(logging.WARNING)
    assert 3 == len(info)
    try:
        logger.critical("Now go boom")
        raise Exception("Should not get here")
    except ZeroDivisionError:
        pass
    logger.warning("This is a warning")
    info = store.retreive_log_messages(logging.WARNING)
    # an error disables the logstore for safety
    # includes the ones before setting the log
    assert store.retreive_log_messages() == \
           [(30, 'This is early'), (20, 'Pre info'),
            (30, 'This is a warning'), (40, 'And an Error'),
            (20, 'This is an info')]

    assert 3 == len(store.retreive_log_messages(logging.WARNING))
    # Only the ones from after the log store turned off
    # the error, the critical and the last warning
    assert 3 == len(FormatAdapter._pop_not_logged_messages())


def test_bad_log_store():
    logger = FormatAdapter(logging.getLogger(__name__))
    try:
        logger.set_log_store("bacon")
        raise Exception("bad call accepted")
    except TypeError:
        pass
