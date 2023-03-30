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


class ResetStatus(Enum):
    """
    Different states the reset could be in.

    This class is design to used internally by UtilsDataView.
    """
    NOT_SETUP = (0)
    SETUP = (1)
    HAS_RUN = (2)
    SOFT_RESET = (3)
    HARD_RESET = (4)

    def __new__(cls, value):
        # pylint: disable=protected-access
        obj = object.__new__(cls)
        obj._value_ = value
        return obj
