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

import datetime


class Timer(object):
    """ A timer used for performance measurements.

    Recommended usage::

        with Timer() as timer:
            ... do stuff that takes time ...

        elapsed_time = timer.measured_interval

    or alternatively::

        timer = Timer()
        timer.start_timing()
        ... do stuff that takes time ...
        elapsed_time = timer.take_sample()

    Mixing these two styles is *not recommended*.
    """

    __slots__ = [

        # The start time when the timer was set off
        "_start_time",

        # The time in the measured section
        "_measured_section_interval"
    ]

    def __init__(self):
        self._start_time = None
        self._measured_section_interval = None

    def start_timing(self):
        """ Start the timing. Use :py:meth:`take_sample` to get the end.
        """
        self._start_time = datetime.datetime.now()

    def take_sample(self):
        """ Describes how long has elapsed since the instance that the\
            :py:meth:`start_timing` method was last called.

        :rtype: datetime.timedelta
        """
        time_now = datetime.datetime.now()
        diff = time_now - self._start_time
        return diff

    def __enter__(self):
        self.start_timing()
        return self

    def __exit__(self, *_args):
        self._measured_section_interval = self.take_sample()
        return False

    @property
    def measured_interval(self):
        """ Get how long elapsed during the measured section.

        :rtype: datetime.timedelta
        """
        return self._measured_section_interval
