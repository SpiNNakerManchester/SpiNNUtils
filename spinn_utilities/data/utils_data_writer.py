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

import os.path

from spinn_utilities.exceptions import InvalidDirectory
from .data_status import Data_Status
from .utils_data_view import UtilsDataView, _UtilsDataModel


class UtilsDataWriter(UtilsDataView):
    """
    Writer class for the Fec Data

    """
    __data = _UtilsDataModel()
    __slots__ = []

    def mock(self):
        """
        Clears out all data and adds mock values where needed.

        This should set the most likely defaults values.
        But be aware that what is considered the most likely default could
        change over time.

        Unittests that depend on any valid value being set should be able to
        depend on Mock.

        Unittest that depend on a specific value should call mock and then
        set that value.
        """
        self.__data._clear()
        self.__data._status = Data_Status.MOCKED

    def setup(self):
        """
        Puts all data back into the state expected at sim.setup time

        """
        self.__data._clear()
        self.__data._status = Data_Status.SETUP

    def start_run(self):
        """
        Puts all data into the state expected after do_run_loop started

        """
        self.__data._status = Data_Status.IN_RUN

    def finish_run(self):
        """
        Puts all data into the state expected after sim.run

        """
        self.__data._status = Data_Status.FINISHED

    def hard_reset(self):
        """
        Puts all data back into the state expected at graph changed and
            sim.reset

        This resets any data set after sim.setup has finished
        """
        self.__data._hard_reset()
        # self.__utils_data._status = Data_Status.HARD_RESET

    def soft_reset(self):
        """
        Puts all data back into the state expected at sim.reset but not
        graph changed

        """
        self.__data._soft_reset()

    def stopping(self):
        """
        Puts all data into the state expected during stop

        """
        self.__data._status = Data_Status.STOPPING

    def shut_down(self):
        """
        Puts all data into the state expected after sim.end

        """
        self.__data._status = Data_Status.SHUTDOWN

    def set_run_dir_path(self, run_dir_path):
        """
        Checks and sets the run_dir_path

        :param str run_dir_path:
        """
        if os.path.isdir(run_dir_path):
            self.__data._run_dir_path = run_dir_path
        else:
            self.__data._run_dir_path = None
            raise InvalidDirectory("run_dir_path", run_dir_path)
