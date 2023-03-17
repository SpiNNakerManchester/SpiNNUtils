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
import sys
import time
from datetime import timedelta

if sys.version_info >= (3, 7):
    # acquire the most accurate measurement available (perf_counter_ns)
    _now = time.perf_counter_ns
    # conversion factor
    _NANO_TO_MICRO = 1000.0

    def _convert_to_timedelta(time_diff):
        """
        Have to convert to a timedelta for rest of code to read.

        As perf_counter_ns is nano seconds, and time delta lowest is micro,
        need to convert.
        """
        return timedelta(microseconds=time_diff / _NANO_TO_MICRO)

else:
    # acquire the most accurate measurement available (perf_counter)
    _now = time.perf_counter

    def _convert_to_timedelta(time_diff):
        """
        Have to convert to a timedelta for rest of code to read.

        As perf_counter is fractional seconds, put into correct time delta.
        """
        return timedelta(seconds=time_diff)


class Timer(object):
    """
    A timer used for performance measurements.

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
        """
        Start the timing. Use :py:meth:`take_sample` to get the end.
        """
        self._start_time = _now()

    def take_sample(self):
        """
        Describes how long has elapsed since the instance that the
        :py:meth:`start_timing` method was last called.

        :rtype: datetime.timedelta
        """
        time_now = _now()
        diff = time_now - self._start_time
        return _convert_to_timedelta(diff)

    def __enter__(self):
        self.start_timing()
        return self

    def __exit__(self, *_args):
        self._measured_section_interval = self.take_sample()
        return False

    @property
    def measured_interval(self):
        """
        Get how long elapsed during the measured section.

        :rtype: datetime.timedelta
        """
        return self._measured_section_interval
