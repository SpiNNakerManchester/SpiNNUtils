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

import os.path

import logging
from spinn_utilities.exceptions import (
    IllegalWriterException, InvalidDirectory, SimulatorNotRunException,
    UnexpectedStateChange)
from spinn_utilities.log import FormatAdapter
from .data_status import DataStatus
from .reset_status import ResetStatus
from .run_status import RunStatus
from .utils_data_view import UtilsDataView, _UtilsDataModel

logger = FormatAdapter(logging.getLogger(__file__))
# pylint: disable=protected-access


class UtilsDataWriter(UtilsDataView):
    """
    Writer class for the information in UtilsDataView

    This and subclass Writers are specifically designed to be used by the
    simulators (ASB) and unitests only!
    Any other usage is not supported.

    The Writers are specifically designed to support only one instant
    (typically held by ASB as self._data_writer).

    Creating a new instant of the Writer will clear out any data added by the
    previous instance.

    Unittest can create a writer by doing ...Writer.mock() or Writer.setup()
    The mock method adds some default data such as directories and
    a Virtual 8 * 8 Machine, as well as allowing some backdoor methods.
    ...Writer.mock() is the recommnded one for unittests
    setup() is more like what ASB does and allows for state changes such as
    writer.start_running

    ASB init (or it sub classes) will create a new writer
    so a call to sim.setup will clear all previously held data

    As the Writers are not designed for general usage the methods can change
    without notice.

    """
    __data = _UtilsDataModel()
    __slots__ = []

    def __init__(self, state):
        """
        Creates a new writer clearing all previous data and sets the state

        :param Data_Status state: State writer should be in
        """
        if state == DataStatus.MOCKED:
            self._mock()
        elif state == DataStatus.SETUP:
            self._setup()
        else:
            raise IllegalWriterException(
                "Writers can only be created by mock or setup")

    @classmethod
    def mock(cls):
        """
        Creates a writer in mock mode.

        All previous data will be cleared

        This should set the most likely defaults values.
        But be aware that what is considered the most likely default could
        change over time.

        Unittests that depend on any valid value being set should be able to
        depend on Mock.

        Unittest that depend on a specific value should call mock and then
        set that value.

        :return: A Data Writer
        :rtype: UtilsDataWriter
        """
        return cls(DataStatus.MOCKED)

    @classmethod
    def setup(cls):
        """
        Creates a writer in normal mode.

        All previous data will be cleared

        :return: A Data Writer
        :rtype: UtilsDataWriter
        """
        return cls(DataStatus.SETUP)

    def _mock(self):
        """
        This method should only be called by mock (via init)

        """
        self.__data._clear()
        self.__data._data_status = DataStatus.MOCKED
        self.__data._reset_status = ResetStatus.NOT_SETUP
        self.__data._run_status = RunStatus.NOT_SETUP

    def _setup(self):
        """
        This method should only be called by setup (via init)

        """
        self.__data._clear()
        self.__data._data_status = DataStatus.SETUP
        self.__data._reset_status = ResetStatus.SETUP
        self.__data._run_status = RunStatus.NOT_RUNNING

    def start_run(self):
        """
        Puts all data into the state expected after do_run_loop started

        """
        if self.__data._run_status != RunStatus.NOT_RUNNING:
            self.check_valid_simulator()
            raise UnexpectedStateChange(
                f"Unexpected start run when in run state "
                f"{self.__data._run_status}")
        self.__data._run_status = RunStatus.IN_RUN

    def finish_run(self):
        """
        Puts all data into the state expected after sim.run ends

        """
        if self.__data._run_status not in [
                RunStatus.IN_RUN, RunStatus.STOP_REQUESTED]:
            self.check_valid_simulator()
            raise UnexpectedStateChange(
                f"Unexpected finish run when in run state "
                f"{self.__data._run_status}")
        self.__data._run_status = RunStatus.NOT_RUNNING
        self.__data._reset_status = ResetStatus.HAS_RUN

    def _hard_reset(self):
        """
        This method should only be called by hard_setup.
        """
        self.__data._hard_reset()
        self.__data._reset_status = ResetStatus.HARD_RESET

    def hard_reset(self):
        """
        Puts all data back into the state expected at graph changed and
            sim.reset

        This resets any data set after sim.setup has finished
        """
        if self.__data._run_status not in [
                RunStatus.IN_RUN, RunStatus.STOP_REQUESTED]:
            self.check_user_can_act()
        if self.__data._reset_status in [
                ResetStatus.HAS_RUN,
                ResetStatus.SOFT_RESET]:
            # call the protected method at the highest possible level
            self._hard_reset()
            return
        self.check_valid_simulator()
        if self.__data._reset_status == ResetStatus.SETUP:
            raise SimulatorNotRunException(
                "Calling reset before calling run is not supported")
        raise UnexpectedStateChange(
            f"Unexpected call to reset while reset status is "
            f"{self.__data._reset_status}")

    def _soft_reset(self):
        """
        This method should only be called from soft_reset

        """
        self.__data._soft_reset()
        self.__data._reset_status = ResetStatus.SOFT_RESET

    def soft_reset(self):
        """
        Puts all data back into the state expected at sim.reset but not
        graph changed

        """
        self.check_user_can_act()
        if self.__data._reset_status == ResetStatus.HAS_RUN:
            # call the protected method at the highest possible level
            self._soft_reset()
            return
        self.check_valid_simulator()
        if self.__data._reset_status == ResetStatus.SETUP:
            raise SimulatorNotRunException(
                "Calling reset before calling run is not supported")
        raise UnexpectedStateChange(
            f"Unexpected call to reset while reset status is "
            f"{self.__data._reset_status}")

    def request_stop(self):
        """
        Used to indicate a user has requested a stop.

        This is expected to be called during run from a different thread.
        """
        if self.__data._run_status != RunStatus.IN_RUN:
            self.check_valid_simulator()
            raise UnexpectedStateChange(
                f"Unexpected request stop when in run state "
                f"{self.__data._run_status}")
        self.__data._run_status = RunStatus.STOP_REQUESTED

    def stopping(self):
        """
        Puts all data into the state expected during stop

        :raises SimulatorNotSetupException: If called before sim.setup
        :raises SimulatorShutdownException: If called after sim.end
        """
        if self.__data._run_status not in [
                RunStatus.NOT_RUNNING, RunStatus.IN_RUN,
                RunStatus.STOP_REQUESTED]:
            self.check_valid_simulator()
            raise UnexpectedStateChange(
                "Unexpected call to stopping while in run_state"
                f" {self.__data._run_status}")
        self.__data._run_status = RunStatus.STOPPING

    def shut_down(self):
        """
        Puts all data into the state expected after sim.end

        Most methods that change data, or state will raise an exception after
        this call.

        Most data however will still be available.

        """
        self.__data._data_status = DataStatus.SHUTDOWN
        self.__data._run_status = RunStatus.SHUTDOWN

    def set_run_dir_path(self, run_dir_path):
        """
        Checks and sets the run_dir_path

        :param str run_dir_path:
        :raises InvalidDirectory: if the run_dir_path is not a directory
        """
        if os.path.isdir(run_dir_path):
            self.__data._run_dir_path = run_dir_path
        else:
            self.__data._run_dir_path = None
            raise InvalidDirectory("run_dir_path", run_dir_path)

    def set_report_dir_path(self, reports_dir_path):
        """
        Checks and sets the reoprts_dir_path

        :param str reprots_dir_path:
        :raises InvalidDirectory: if the reports_dir_path is not a directory
        """
        if os.path.isdir(reports_dir_path):
            self.__data._report_dir_path = reports_dir_path
        else:
            self.__data._report_dir_path = None
            raise InvalidDirectory("run_dir_path", reports_dir_path)

    def _set_executable_finder(self, executable_finder):
        """
        Only usable by unittests!

        :param executable_finder:
        :return:
        """
        if not self._is_mocked():
            raise NotImplementedError("Only valid in Mocked state!")
        self.__data._executable_finder = executable_finder
