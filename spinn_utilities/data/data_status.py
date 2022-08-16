# Copyright (c) 2021-2022 The University of Manchester
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
