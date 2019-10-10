# Copyright (c) 2017-2019 The University of Manchester
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
import re
try:
    from inspect import getfullargspec
except ImportError:
    # Python 2.7 hack
    from inspect import getargspec as getfullargspec
from .overrides import overrides
from six import PY2

levels = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}


class ConfiguredFilter(object):
    """ Allow a parent logger to filter a child logger.
    """
    __slots__ = [
        "_default_level", "_levels"]

    def __init__(self, conf):
        self._levels = ConfiguredFormatter.construct_logging_parents(conf)
        self._default_level = levels[conf.get("Logging", "default")]

    def filter(self, record):
        """ Get the level for the deepest parent, and filter appropriately.
        """
        level = ConfiguredFormatter.level_of_deepest_parent(
            self._levels, record.name)

        if level is None:
            return record.levelno >= self._default_level

        return record.levelno >= level


class ConfiguredFormatter(logging.Formatter):
    """ Defines the logging format for the SpiNNaker host software.
    """
    # Precompile this RE; it gets used quite a few times
    __last_component = re.compile(r'\.[^.]+$')

    def __init__(self, conf):
        level = conf.get("Logging", "default")
        if level == "debug":
            super(ConfiguredFormatter, self).__init__(
                fmt="%(asctime)-15s %(levelname)s: %(pathname)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S")
        else:
            super(ConfiguredFormatter, self).__init__(
                fmt="%(asctime)-15s %(levelname)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S")

    @staticmethod
    def construct_logging_parents(conf):
        """ Create a dictionary of module names and logging levels.
        """

        # Construct the dictionary
        _levels = {}

        if not conf.has_section("Logging"):
            return _levels

        for label, level in levels.items():
            if conf.has_option("Logging", label):
                modules = [s.strip() for s in
                           conf.get('Logging', label).split(',')]
                if '' not in modules:
                    _levels.update(dict((m, level) for m in modules))
        return _levels

    @staticmethod
    def deepest_parent(parents, child):
        """ Greediest match between child and parent.
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
        """ The logging level of the greediest match between child and parent.
        """

        # child = re.sub( r'^pacman103\.', '', child )
        parent = ConfiguredFormatter.deepest_parent(parents.keys(), child)

        if parent is None:
            return None

        return parents[parent]


class _BraceMessage(object):
    """ A message that converts a Python format string to a string
    """
    __slots__ = [
        "args", "fmt", "kwargs"]

    def __init__(self, fmt, args, kwargs):
        self.fmt = fmt
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return str(self.fmt).format(*self.args, **self.kwargs)


class FormatAdapter(logging.LoggerAdapter):
    """ An adaptor for logging with messages that uses Python format strings.

    Example::

        log = FormatAdapter(logging.getLogger(__name__))
        log.info("this message has {} inside {}", 123, 'itself')
        # --> INFO: this message has 123 inside itself
    """

    def __init__(self, logger, extra=None):
        if extra is None:
            extra = {}
        super(FormatAdapter, self).__init__(logger, extra)
        self.do_log = logger._log  # pylint: disable=protected-access

    if PY2:
        @overrides(logging.LoggerAdapter.critical)
        def critical(self, msg, *args, **kwargs):
            self.log(logging.CRITICAL, msg, *args, **kwargs)

        @overrides(logging.LoggerAdapter.debug)
        def debug(self, msg, *args, **kwargs):
            self.log(logging.DEBUG, msg, *args, **kwargs)

        @overrides(logging.LoggerAdapter.error)
        def error(self, msg, *args, **kwargs):
            self.log(logging.ERROR, msg, *args, **kwargs)

        @overrides(logging.LoggerAdapter.exception)
        def exception(self, msg, *args, exc_info=True, **kwargs):
            kwargs["exc_info"] = 1
            self.log(logging.ERROR, msg, *args, exc_info=exc_info, **kwargs)

        @overrides(logging.LoggerAdapter.info)
        def info(self, msg, *args, **kwargs):
            self.log(logging.INFO, msg, *args, **kwargs)

        @overrides(logging.LoggerAdapter.warning)
        def warning(self, msg, *args, **kwargs):
            self.log(logging.WARNING, msg, *args, **kwargs)

    @overrides(logging.LoggerAdapter.log, extend_doc=False)
    def log(self, level, msg, *args, **kwargs):
        """ Delegate a log call to the underlying logger, applying appropriate\
            transformations to allow the log message to be written using\
            Python format string, rather than via `%`-substitutions.
        """
        if self.isEnabledFor(level):
            msg, log_kwargs = self.process(msg, kwargs)
            if "exc_info" in kwargs:
                log_kwargs["exc_info"] = kwargs["exc_info"]
            self.do_log(
                level, _BraceMessage(msg, args, kwargs), (), **log_kwargs)

    @overrides(logging.LoggerAdapter.process, extend_doc=False)
    def process(self, msg, kwargs):
        """ Process the logging message and keyword arguments passed in to a\
            logging call to insert contextual information. You can either\
            manipulate the message itself, the keyword arguments or both.\
            Return the message and *kwargs* modified (or not) to suit your\
            needs.
        """
        # pylint: disable=deprecated-method
        return msg, {
            key: kwargs[key]
            for key in getfullargspec(self.do_log).args[1:]
            if key in kwargs}
