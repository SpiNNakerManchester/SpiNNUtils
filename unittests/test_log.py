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
from spinn_utilities.log import (
    _BraceMessage, ConfiguredFilter, ConfiguredFormatter, FormatAdapter,
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
    logger._pop_not_stored_messages()  # clear the log
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
    assert len(logger._pop_not_stored_messages())


def test_logger_dict():
    log = MockLog()
    logger = FormatAdapter(log)
    mydict = {1: "one", 2: "two"}
    logger.info(mydict)
    assert str(log.last_msg) == "{1: 'one', 2: 'two'}"


def test_logger_exception():
    log = MockLog()
    logger = FormatAdapter(log)
    logger._pop_not_stored_messages()  # clear the log

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
    assert len(logger._pop_not_stored_messages()) == 1


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
    assert 0 == len(FormatAdapter._pop_not_stored_messages())
    logger.warning("This is a warning")
    logger2.error("And an Error")
    logger.info("This is an {}", "info")
    info = store.retreive_log_messages(logging.WARNING)
    assert 3 == len(info)
    try:
        logger.critical("Now go boom")
        raise NotImplementedError("Should not get here")
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
    assert 3 == len(FormatAdapter._pop_not_stored_messages())


def test_bad_log_store():
    logger = FormatAdapter(logging.getLogger(__name__))
    try:
        logger.set_log_store("bacon")
        raise NotImplementedError("bad call accepted")
    except TypeError:
        pass


class DoKeyError(object):

    def __str__(self):
        raise KeyError("Boom!")


class DoIndexError(object):

    def __str__(self):
        raise IndexError("Boom!")


def test_brace_message():
    bm = _BraceMessage("This is a {name_one}", [], {"name_one": "test"})
    assert str(bm) == "This is a test"
    bm = _BraceMessage("This is a {name_one}", [], {})
    assert str(bm) == "This is a {name_one}"
    bm = _BraceMessage("This is a {name_one}", [], {"name_two": "not me"})
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
