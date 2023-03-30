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

import atexit
from datetime import datetime
import logging
import re
import sys
from inspect import getfullargspec
from .log_store import LogStore
from .overrides import overrides

_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}


class ConfiguredFilter(object):
    """
    Allow a parent logger to filter a child logger.
    """
    __slots__ = [
        "_default_level", "_levels"]

    def __init__(self, conf):
        self._levels = ConfiguredFormatter.construct_logging_parents(conf)
        self._default_level = _LEVELS[conf.get("Logging", "default")]

    def filter(self, record):
        """
        Get the level for the deepest parent, and filter appropriately.
        """
        level = ConfiguredFormatter.level_of_deepest_parent(
            self._levels, record.name)

        if level is None:
            return record.levelno >= self._default_level

        return record.levelno >= level


class ConfiguredFormatter(logging.Formatter):
    """
    Defines the logging format for the SpiNNaker host software.
    """
    # Precompile this RE; it gets used quite a few times
    __last_component = re.compile(r'\.[^.]+$')

    def __init__(self, conf):
        if conf.get("Logging", "default") == "debug":
            fmt = "%(asctime)-15s %(levelname)s: %(pathname)s: %(message)s"
        else:
            fmt = "%(asctime)-15s %(levelname)s: %(message)s"
        super().__init__(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S")

    @staticmethod
    def construct_logging_parents(conf):
        """
        Create a dictionary of module names and logging levels.
        """
        # Construct the dictionary
        _levels = {}

        if not conf.has_section("Logging"):
            return _levels

        for label, level in _LEVELS.items():
            if conf.has_option("Logging", label):
                modules = [s.strip() for s in
                           conf.get('Logging', label).split(',')]
                if '' not in modules:
                    _levels.update(dict((m, level) for m in modules))
        return _levels

    @staticmethod
    def deepest_parent(parents, child):
        """
        Greediest match between child and parent.
        """
        # TODO: this can almost certainly be neater!
        # Repeatedly strip elements off the child until we match an item in
        # parents
        match = child

        while '.' in match and match not in parents:
            match = ConfiguredFormatter.__last_component.sub('', match)

        # If no match then return None, there is no deepest parent
        if match not in parents:
            match = None

        return match

    @staticmethod
    def level_of_deepest_parent(parents, child):
        """
        The logging level of the greediest match between child and parent.
        """
        # child = re.sub( r'^pacman103\.', '', child )
        parent = ConfiguredFormatter.deepest_parent(parents.keys(), child)

        if parent is None:
            return None

        return parents[parent]


class _BraceMessage(object):
    """
    A message that converts a Python format string to a string.
    """
    __slots__ = [
        "args", "fmt", "kwargs"]

    def __init__(self, fmt, args, kwargs):
        self.fmt = fmt
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        try:
            return str(self.fmt).format(*self.args, **self.kwargs)
        except KeyError:
            try:
                if (not self.args and not self.kwargs and
                        isinstance(self.fmt, str)):
                    # nothing to format with so assume brackets not formatting
                    return self.fmt
                return "KeyError: " + str(self.fmt)
            except KeyError:
                return "Double KeyError"
        except IndexError:
            try:
                if self.args or self.kwargs:
                    return "IndexError: " + str(self.fmt)
                else:
                    # nothing to format with so assume brackets not formatting
                    return str(self.fmt)
            except IndexError:
                return "Double IndexError"


class LogLevelTooHighException(Exception):
    """
    An Exception throw when the System tries to log at a level where an
    Exception is a better option.
    """


class FormatAdapter(logging.LoggerAdapter):
    """
    An adaptor for logging with messages that uses Python format strings.

    Example::

        log = FormatAdapter(logging.getLogger(__name__))
        log.info("this message has {} inside {}", 123, 'itself')
        # --> INFO: this message has 123 inside itself
    """
    __kill_level = logging.CRITICAL + 1
    __repeat_at_end = logging.WARNING
    __not_stored_messages = []
    __log_store = None

    @classmethod
    def set_kill_level(cls, level=None):
        """
        Allow system to change the level at which a log is changed to an
        Exception.

        .. note::
            This is a static method; it affects all log messages.

        :param int level:
            The level to set. The values in :py:mod:`logging` are recommended.
        """
        if level is None:
            cls.__kill_level = logging.CRITICAL + 1
        else:
            cls.__kill_level = level

    @classmethod
    def set_log_store(cls, log_store):
        if not isinstance(log_store, (type(None), LogStore)):
            raise TypeError("log_store must be a LogStore")
        cls.__log_store = log_store
        for timestamp, level, message in cls._pop_not_stored_messages():
            cls.__log_store.store_log(level, message, timestamp)

    def __init__(self, logger, extra=None):
        if extra is None:
            extra = {}
        super().__init__(logger, extra)
        self.do_log = logger._log  # pylint: disable=protected-access

    @overrides(logging.LoggerAdapter.log, extend_doc=False)
    def log(self, level, msg, *args, **kwargs):
        """
        Delegate a log call to the underlying logger, applying appropriate
        transformations to allow the log message to be written using
        Python format string, rather than via `%`-substitutions.
        """
        if level >= FormatAdapter.__kill_level:
            raise LogLevelTooHighException(_BraceMessage(msg, args, kwargs))
        if self.isEnabledFor(level):
            message = _BraceMessage(msg, args, kwargs)
            if self.__log_store:
                try:
                    FormatAdapter.__log_store.store_log(level, str(message))
                except Exception as ex:
                    # Avoid an endless loop of log store errors being logged
                    self.__not_stored_messages.append((
                        datetime.now(),
                        level,
                        f"Unable to store log messages in database due to"
                        f" {ex}"))
                    self.__not_stored_messages.append(
                        (datetime.now(), level, str(message)))
                    FormatAdapter.__log_store = None
                    raise
            else:
                self.__not_stored_messages.append(
                    (datetime.now(), level, str(message)))
            msg, log_kwargs = self.process(msg, kwargs)
            if "exc_info" in kwargs:
                log_kwargs["exc_info"] = kwargs["exc_info"]
            self.do_log(level, message, (), **log_kwargs)

    @overrides(logging.LoggerAdapter.process, extend_doc=False)
    def process(self, msg, kwargs):
        """
        Process the logging message and keyword arguments passed in to a
        logging call to insert contextual information. You can either
        manipulate the message itself, the keyword arguments or both.
        Return the message and *kwargs* modified (or not) to suit your needs.
        """
        return msg, {
            key: kwargs[key]
            for key in getfullargspec(self.do_log).args[1:]
            if key in kwargs}

    @classmethod
    def atexit_handler(cls):
        messages = []
        if cls.__log_store:
            try:
                messages = cls.__log_store.retreive_log_messages(
                    cls.__repeat_at_end)
            except Exception:  # pylint: disable=broad-except
                pass

        messages.extend(cls._pop_not_stored_messages(cls.__repeat_at_end))
        if messages:
            level = logging.getLevelName(cls.__repeat_at_end)
            print(f"\n!WARNING: {len(messages)} log messages were "
                  f"generated at level {level} or above.", file=sys.stderr)
            print("This may mean that the results are invalid.",
                  file=sys.stderr)
            if cls.__log_store:
                print(f"You are advised to check the details of these in "
                      f"the p_log_view of : "
                      f"{cls.__log_store.get_location()}", file=sys.stderr)
            if len(messages) < 10:
                print("These are:", file=sys.stderr)
            else:
                print("The first 10 are:", file=sys.stderr)
            for message in messages[0:10]:
                print(message, file=sys.stderr)

    @classmethod
    def _pop_not_stored_messages(cls, min_level=0):
        """
        Returns the log of messages to print on exit and
        *clears that log*.

        .. note::
            Should only be called externally from test code!
        """
        result = []
        try:
            for timestamp, level, message in cls.__not_stored_messages:
                if level >= min_level:
                    result.append((timestamp, level, message))
            return result
        except Exception:  # pylint: disable=broad-except
            return result
        finally:
            cls.__not_stored_messages = []


atexit.register(FormatAdapter.atexit_handler)
