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
from typing import Type, Tuple
from spinn_utilities.exceptions import (
    DataNotMocked, DataNotYetAvialable, NotSetupException, ShutdownException,
    SpiNNUtilsException)


class DataStatus(Enum):
    """
    Different states the Data can be in.

    This class is designed to used internally by UtilsDataView
    """
    #: No setup calls have been done yet.
    NOT_SETUP = (0, NotSetupException)
    #: The system is (to be) setup in mocked mode for unit testing.
    MOCKED = (1, DataNotMocked)
    #: The system is (to be) setup for running user code.
    SETUP = (2, DataNotYetAvialable)
    #: The system has been shut down.
    SHUTDOWN = (3, ShutdownException)

    def __new__(cls, *args: Tuple[int, SpiNNUtilsException]) -> 'DataStatus':
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, value: int, exception: Type[SpiNNUtilsException]):
        # use argument
        _ = value
        self._exception = exception

    def exception(self, data: str) -> SpiNNUtilsException:
        """
        Returns an instance of the most suitable data-not-available exception.

        :param data: Parameter to pass to the relevant constructor.
         """
        return self._exception(data)
