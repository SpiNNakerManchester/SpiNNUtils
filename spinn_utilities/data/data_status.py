# Copyright (c) 2017-2019 The University of Manchester
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


class Data_Status(Enum):
    """ Different states the Data can be in.
    """
    NOT_SETUP = (0, NotSetupException)
    MOCKED = (1, DataNotMocked)
    SETUP = (2, DataNotYetAvialable)
    # HARD_RESET = (3, DataChanged)
    IN_RUN = (4, DataNotYetAvialable)
    FINISHED = (5, DataNotYetAvialable)
    STOPPING = (6, ShutdownException)
    SHUTDOWN = (7, ShutdownException)

    def __new__(cls, value, exception):
        # pylint: disable=protected-access
        obj = object.__new__(cls)
        obj._value_ = value
        obj._exception = exception
        return obj

    def exception(self, data):
        return self._exception(data)
