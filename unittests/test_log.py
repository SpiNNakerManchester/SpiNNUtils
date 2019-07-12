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
from spinn_utilities.log import FormatAdapter


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


def test_logger_exception():
    log = MockLog()
    logger = FormatAdapter(log)

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
