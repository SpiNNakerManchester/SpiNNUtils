# Copyright (c) 2021-2022 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
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
    NOT_SETUP = (0, NotSetupException)
    MOCKED = (1, DataNotMocked)
    SETUP = (2, DataNotYetAvialable)
    SHUTDOWN = (3, ShutdownException)

    def __new__(cls, value, exception):
        # pylint: disable=protected-access
        obj = object.__new__(cls)
        obj._value_ = value
        obj._exception = exception
        return obj

    def exception(self, data):
        """
        Returns the most suitable data not available exception

        :param data:
        :rtype: ~pinn_utilities.exceptions.SpiNNUtilsException
        """
        return self._exception(data)
