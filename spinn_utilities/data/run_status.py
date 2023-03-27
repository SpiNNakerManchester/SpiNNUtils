# Copyright (c) 2021 The University of Manchester
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

from enum import Enum


class RunStatus(Enum):
    """
    Different states the run could be in.

    This is from the perspective of the users script.
    It says nothing about if there is C code running,
    i.e., has a `sim.run` (or similar) call started but not yet returned.

    This is combined with the :py:class:`ResetStatus` to get the needed status.

    This class is design to used internally by :py:class:`UtilsDataView`.
    """
    NOT_SETUP = (0)
    NOT_RUNNING = (12)
    IN_RUN = (2)
    STOP_REQUESTED = (3)
    STOPPING = (4)
    SHUTDOWN = (5)

    def __new__(cls, value):
        # pylint: disable=protected-access
        obj = object.__new__(cls)
        obj._value_ = value
        return obj
