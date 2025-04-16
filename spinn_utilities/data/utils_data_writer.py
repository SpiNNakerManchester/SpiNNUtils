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
from __future__ import annotations
import atexit
import datetime
import os.path
import logging
import time
from typing_extensions import Optional, Self

from spinn_utilities.config_holder import get_config_str
from spinn_utilities.exceptions import (
    IllegalWriterException, InvalidDirectory, SimulatorNotRunException,
    UnexpectedStateChange)
from spinn_utilities.executable_finder import ExecutableFinder
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
    simulators (ASB) and unit tests only!
    Any other usage is not supported.

    The Writers are specifically designed to support only one instant
    (typically held by ASB as `self._data_writer`).

    Creating a new instant of the Writer will clear out any data added by the
    previous instance.

    Unit tests can create a writer by doing `...Writer.mock()` or
    `Writer.setup()`.
    The `mock` method adds some default data such as directories and
    a Virtual 8 * 8 Machine, as well as allowing some back-door methods.
    `...Writer.mock()` is the recommended one for unit tests;
    `setup()` is more like what ASB does and allows for state changes such as
    `writer.start_running`.

    ASB `__init__()` (or it subclasses) will create a new writer
    so a call to `sim.setup` will clear all previously held data.

    .. warning::
        As the Writers are not designed for general usage the methods can
        change without notice.
    """
    __data = _UtilsDataModel()
    __slots__ = ()

    REPORTS_DIRNAME = "reports"
    ERRORED_FILENAME = "errored"
    FINISHED_FILENAME = "finished"

    def __init__(self, state: DataStatus):
        """
        :param state: State writer should be in
        """
        if state == DataStatus.MOCKED:
            self._mock()
        elif state == DataStatus.SETUP:
            self._setup()
        else:
            raise IllegalWriterException(
                "Writers can only be created by mock or setup")

    @classmethod
    def mock(cls) -> Self:
        """
        Creates a writer in mock mode.

        All previous data will be cleared.

        This should set the most likely defaults values.
        But be aware that what is considered the most likely default could
        change over time.

        Unit tests that depend on any valid value being set should be able to
        depend on Mock.

        A unit test that depends on a specific value should call `mock()` and
        then set that value.

        :return: A Data Writer
        """
        return cls(DataStatus.MOCKED)

    @classmethod
    def setup(cls) -> Self:
        """
        Creates a writer in normal mode.

        All previous data will be cleared

        :return: A Data Writer
        """
        return cls(DataStatus.SETUP)

    def _mock(self) -> None:
        """
        This method should only be called by `mock` (via `__init__`).
        """
        self.__data._clear()
        self.__data._data_status = DataStatus.MOCKED
        self.__data._reset_status = ResetStatus.NOT_SETUP
        # run numbers start at 1 and when not running this is the next one
        self.__data._run_number = 1
        self.__data._run_status = RunStatus.NOT_SETUP

    def _setup(self) -> None:
        """
        This method should only be called by `setup` (via `__init__`).
        """
        self.__data._clear()
        self.__data._data_status = DataStatus.SETUP
        self.__data._reset_status = ResetStatus.SETUP
        # run numbers start at 1 and when not running this is the next one
        self.__data._run_number = 1
        self.__data._run_status = RunStatus.NOT_RUNNING
        self.__create_reports_directory()
        self.__create_timestamp_directory()
        self.__create_run_dir_path()

    def start_run(self) -> None:
        """
        Puts all data into the state expected after `do_run_loop` started.
        """
        if self.__data._run_status != RunStatus.NOT_RUNNING:
            self.check_valid_simulator()
            raise UnexpectedStateChange(
                f"Unexpected start run when in run state "
                f"{self.__data._run_status}")
        self.__data._run_status = RunStatus.IN_RUN

    def finish_run(self) -> None:
        """
        Puts all data into the state expected after `sim.run` ends.
        """
        if self.__data._run_status not in [
                RunStatus.IN_RUN, RunStatus.STOP_REQUESTED]:
            self.check_valid_simulator()
            raise UnexpectedStateChange(
                f"Unexpected finish run when in run state "
                f"{self.__data._run_status}")
        assert self.__data._run_number is not None
        self.__data._run_number += 1
        self.__data._run_status = RunStatus.NOT_RUNNING
        self.__data._reset_status = ResetStatus.HAS_RUN
        self.__data._requires_data_generation = False
        self.__data._requires_mapping = False

    def _hard_reset(self) -> None:
        """
        This method should only be called by `hard_setup`.
        """
        self.__data._hard_reset()
        if self.is_ran_last():
            self.__data._reset_number += 1
        self.__data._reset_status = ResetStatus.HARD_RESET

    def hard_reset(self) -> None:
        """
        Puts all data back into the state expected at graph changed and
        `sim.reset`.

        This resets any data set after `sim.setup` has finished.
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

    def _soft_reset(self) -> None:
        """
        This method should only be called from `soft_reset`.
        """
        self.__data._soft_reset()
        if self.is_ran_last():
            self.__data._reset_number += 1
        self.__data._reset_status = ResetStatus.SOFT_RESET

    def soft_reset(self) -> None:
        """
        Puts all data back into the state expected at `sim.reset` but where the
        graph has not changed.
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

    def request_stop(self) -> None:
        """
        Used to indicate a user has requested a stop.

        This is expected to be called during `run` from a different thread.
        """
        if self.__data._run_status != RunStatus.IN_RUN:
            self.check_valid_simulator()
            raise UnexpectedStateChange(
                f"Unexpected request stop when in run state "
                f"{self.__data._run_status}")
        self.__data._run_status = RunStatus.STOP_REQUESTED

    def stopping(self) -> None:
        """
        Puts all data into the state expected during stop.

        :raises SimulatorNotSetupException: If called before `sim.setup`
        :raises SimulatorShutdownException: If called after `sim.end`
        """
        if self.__data._run_status not in [
                RunStatus.NOT_RUNNING, RunStatus.IN_RUN,
                RunStatus.STOP_REQUESTED]:
            self.check_valid_simulator()
            raise UnexpectedStateChange(
                "Unexpected call to stopping while in run_state"
                f" {self.__data._run_status}")
        self.__data._run_status = RunStatus.STOPPING

    def shut_down(self) -> None:
        """
        Puts all data into the state expected after `sim.end`.

        Most methods that change data, or state will raise an exception after
        this call.

        Most data however will still be available.
        """
        self.__data._data_status = DataStatus.SHUTDOWN
        self.__data._run_status = RunStatus.SHUTDOWN

    def get_report_dir_path(self) -> str:
        """
        Returns path to existing reports directory.

        This is the high level directory which in which `timestamp` directories
        and `run` directories are placed.

        As it is only accessed to create `timestamp` directories and
        remove old reports, this is not a view method.

        :raises SpiNNUtilsException:
            If the `simulation_time_step` is currently unavailable
        """
        if self.__data._report_dir_path:
            return self.__data._report_dir_path
        raise self._exception("report_dir_path")

    def set_run_dir_path(self, run_dir_path: str) -> None:
        """
        Checks and sets the `run_dir_path`.

        :param run_dir_path:
        :raises InvalidDirectory: if the `run_dir_path` is not a directory
        """
        if os.path.isdir(run_dir_path):
            self.__data._run_dir_path = run_dir_path
        else:
            self.__data._run_dir_path = None
            raise InvalidDirectory("run_dir_path", run_dir_path)

    def set_report_dir_path(self, reports_dir_path: str) -> None:
        """
        Checks and sets the `reports_dir_path`.

        :param reports_dir_path:
        :raises InvalidDirectory: if the `reports_dir_path` is not a directory
        """
        if os.path.isdir(reports_dir_path):
            self.__data._report_dir_path = reports_dir_path
        else:
            self.__data._report_dir_path = None
            raise InvalidDirectory("run_dir_path", reports_dir_path)

    def __create_run_dir_path(self) -> None:
        self.set_run_dir_path(self._child_folder(
            self.get_timestamp_dir_path(),
            f"run_{self.get_run_number()}"))

    def __create_reports_directory(self) -> None:
        default_report_file_path = get_config_str(
            "Reports", "default_report_file_path")
        # determine common report folder
        if default_report_file_path == "DEFAULT":
            directory = os.getcwd()
        else:
            directory = default_report_file_path
        # global reports folder
        self.set_report_dir_path(
            self._child_folder(directory, self.REPORTS_DIRNAME))

    @classmethod
    def _get_timestamp(cls) -> str:
        now = datetime.datetime.now()
        return (
            f"{now.year:04}-{now.month:02}-{now.day:02}-{now.hour:02}"
            f"-{now.minute:02}-{now.second:02}-{now.microsecond:06}")

    def __create_timestamp_directory(self) -> None:
        while True:
            try:
                self.__data._timestamp_dir_path = self._child_folder(
                    self.get_report_dir_path(), self._get_timestamp(),
                    must_create=True)
                atexit.register(UtilsDataWriter.write_errored_file)
                return
            except OSError:
                time.sleep(0.5)

    @classmethod
    def write_errored_file(cls, message: Optional[str] = None) -> None:
        """
        Writes an ``errored`` file that signals code if the code has errored

        Not written if there is a finished file exists and
        there is no error message.

        This file signals the report directory can be removed.

        This method can be called while there is still code to be run BUT
        if running other simulations at the same time there is a possibility
        that the report directory is no longer available for writing to.

        :param message: An error message to included
        """
        errored_file_name = os.path.join(
            cls.get_timestamp_dir_path(), cls.ERRORED_FILENAME)

        if message is None:
            finished_file_name = os.path.join(
                cls.get_timestamp_dir_path(), cls.FINISHED_FILENAME)
            if os.path.exists(finished_file_name):
                return

            if os.path.exists(errored_file_name):
                return

            message = "Unexpected end"

        with open(errored_file_name, "w", encoding="utf-8") as f:
            f.writelines(message)
            f.writelines("\n")
            f.writelines(cls._get_timestamp())

    def write_finished_file(self) -> None:
        """
        Write a finished file to flag that the code has finished cleanly

        This file signals the report directory can be removed.
        """
        finished_file_name = os.path.join(
            self.get_timestamp_dir_path(), self.FINISHED_FILENAME)
        with open(finished_file_name, "w", encoding="utf-8") as f:
            f.writelines(self._get_timestamp())

    def _set_executable_finder(
            self, executable_finder: ExecutableFinder) -> None:
        """
        Only usable by unit tests!

        :param ExecutableFinder executable_finder:
        """
        if not self._is_mocked():
            raise NotImplementedError("Only valid in Mocked state!")
        self.__data._executable_finder = executable_finder
