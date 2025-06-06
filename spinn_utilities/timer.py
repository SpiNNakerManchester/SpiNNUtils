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
from datetime import timedelta
from time import perf_counter_ns
from typing import Any, Optional, Tuple
from typing_extensions import Literal

# conversion factor
_NANO_TO_MICRO = 1000.0


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

    def __init__(self) -> None:
        self._start_time: Optional[int] = None
        self._measured_section_interval: Optional[timedelta] = None

    def start_timing(self) -> None:
        """
        Start the timing. Use :py:meth:`take_sample` to get the end.
        """
        self._start_time = perf_counter_ns()

    def take_sample(self) -> timedelta:
        """
        Describes how long has elapsed since the instance that the
        :py:meth:`start_timing` method was last called.
        """
        time_now = perf_counter_ns()
        diff = time_now - (self._start_time or 0)
        return timedelta(microseconds=diff / _NANO_TO_MICRO)

    def __enter__(self) -> 'Timer':
        self.start_timing()
        return self

    def __exit__(self, *_args: Tuple[Any, ...]) -> Literal[False]:
        self._measured_section_interval = self.take_sample()
        return False

    @property
    def measured_interval(self) -> Optional[timedelta]:
        """
        Get how long elapsed during the measured section.
        """
        return self._measured_section_interval
