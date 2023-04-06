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
from spinn_utilities.exceptions import (
    DataNotMocked, DataNotYetAvialable, NotSetupException, ShutdownException)


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

    def __new__(cls, value, exception):
        # pylint: disable=protected-access
        obj = object.__new__(cls)
        obj._value_ = value
        obj._exception = exception
        return obj

    def exception(self, data):
        """
        Returns an instance of the most suitable data-not-available exception.

        :param data: Parameter to pass to the relevant constructor.
        :rtype: ~spinn_utilities.exceptions.SpiNNUtilsException
        """
        return self._exception(data)
