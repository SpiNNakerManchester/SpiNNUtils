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
from spinn_utilities.log import (ConfiguredFilter, ConfiguredFormatter)
from spinn_utilities.log import FormatAdapter, LogLevelTooHighException
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
    def store_log(self, level, message):
        self.data.append((level, message))
        if level == logging.CRITICAL:
            1/0

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
    logger._repeat_log()  # clear the log
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
    assert len(logger._repeat_log()) == 4


def test_logger_dict():
    log = MockLog()
    logger = FormatAdapter(log)
    mydict = {1: "one", 2: "two"}
    logger.info(mydict)
    assert str(log.last_msg) == "{1: 'one', 2: 'two'}"


def test_logger_exception():
    log = MockLog()
    logger = FormatAdapter(log)
    logger._repeat_log()  # clear the log

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
    assert len(logger._repeat_log()) == 1


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
    logger = FormatAdapter(logging.getLogger(__name__))
    logger2 = FormatAdapter(logging.getLogger(__name__))
    store = MockLogStore()
    logger2.set_log_store(store)
    logger.warning("This is a warning")
    logger2.error("And an Error")
    logger.info("This is an info")
    info = store.retreive_log_messages(logging.WARNING)
    assert(2 == len(info))
    try:
        logger.critical("Now go boom")
    except ZeroDivisionError:
        pass
    logger.warning("This is a warning")


def test_bad_log_store():
    logger = FormatAdapter(logging.getLogger(__name__))
    try:
        logger.set_log_store("bacon")
        raise Exception("bad call accepted")
    except TypeError:
        pass
