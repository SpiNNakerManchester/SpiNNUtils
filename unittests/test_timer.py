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

from time import sleep
from spinn_utilities.timer import Timer


def test_create() -> None:
    t = Timer()
    assert t is not None


def test_basic_use() -> None:
    t = Timer()
    # Just check that these things don't throw
    t.start_timing()
    with t:
        sleep(0.1)
    assert t.take_sample() is not None
    assert t.take_sample().total_seconds() > 0


def test_advanced_use() -> None:
    t = Timer()
    with t:
        sleep(0.1)
    assert t.measured_interval is not None
    # In windows it is not always > 0.1
    assert t.measured_interval.total_seconds() >= 0.095
