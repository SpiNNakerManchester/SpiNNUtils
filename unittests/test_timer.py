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

from time import sleep
from spinn_utilities.timer import Timer


def test_create():
    t = Timer()
    assert t is not None


def test_basic_use():
    t = Timer()
    # Just check that these things don't throw
    t.start_timing()
    with t:
        sleep(0.1)
    assert t.take_sample() is not None
    assert t.take_sample().total_seconds() > 0


def test_advanced_use():
    t = Timer()
    with t:
        sleep(0.1)
    assert t.measured_interval is not None
    assert t.measured_interval.total_seconds() >= 0.1
