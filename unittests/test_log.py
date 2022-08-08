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
import tempfile
from spinn_utilities.log import (
    _BraceMessage, ConfiguredFilter, ConfiguredFormatter, FormatAdapter,
    LogLevelTooHighException)


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
    assert len(FormatAdapter._FormatAdapter__repeat_messages) == 4
    FormatAdapter.atexit_handler()
    assert len(FormatAdapter._FormatAdapter__repeat_messages) == 0


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
    fi = ConfiguredFilter(MockConfig1())
    #fi.filter()


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


def test_waning_file():
    log = MockLog()
    logger = FormatAdapter(log)
    log2 = MockLog()
    logger2 = FormatAdapter(log2)
    report_file = tempfile.mktemp()
    logger2.set_report_File(report_file)
    logger.warning("This is a warning")
    logger2.error("And an Error")
    with open(report_file, "r") as myfile:
        data = myfile.readlines()
    assert ("This is a warning\n" in data)
    assert ("And an Error\n" in data)


class DoKeyError(object):

    def __str__(self):
        raise KeyError("Boom!")


class DoIndexError(object):

    def __str__(self):
        raise IndexError("Boom!")


def test_brace_message():
    bm = _BraceMessage("This is a {name_one}", [], {"name_one" : "test"})
    assert str(bm) == "This is a test"
    bm = _BraceMessage("This is a {name_one}", [], {})
    assert str(bm) == "This is a {name_one}"
    bm = _BraceMessage("This is a {name_one}", [], {"name_two" : "not me"})
    assert str(bm) == "KeyError: This is a {name_one}"
    bm = _BraceMessage(DoKeyError(), ["test"], {})
    assert str(bm) == "Double KeyError"

    bm = _BraceMessage("This is a {0}", ["test"], {})
    assert str(bm) == "This is a test"
    bm = _BraceMessage("This is a {0}", [], {})
    assert str(bm) == "This is a {0}"
    bm = _BraceMessage("This is a {1}", ["Zero"], {})
    assert str(bm) == "IndexError: This is a {1}"
    bm = _BraceMessage(DoIndexError(), ["test"], {})
    assert str(bm) == "Double IndexError"

