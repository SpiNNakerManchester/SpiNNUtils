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

import tempfile
from .data_status import DataStatus
from .reset_status import ResetStatus
from .run_status import RunStatus
from spinn_utilities.exceptions import (
    SimulatorNotSetupException, SimulatorRunningException,
    SimulatorShutdownException, UnexpectedStateChange)
from spinn_utilities.executable_finder import ExecutableFinder


class _UtilsDataModel(object):
    """
    Singleton data model

    This class should not be accessed directly please use the DataView and
    DataWriter classes.
    Accessing or editing the data held here directly is NOT SUPPORTED

    There may be other DataModel classes which sit next to this one and hold
    additional data. The DataView and DataWriter classes will combine these
    as needed.

    What data is held where and how can change without notice.
    """

    __singleton = None

    __slots__ = [
        "_data_status",
        "_executable_finder",
        "_reset_status",
        "_run_dir_path",
        "_run_status",
        "_temporary_directory",
    ]

    def __new__(cls):
        if cls.__singleton:
            return cls.__singleton
        # pylint: disable=protected-access
        obj = object.__new__(cls)
        cls.__singleton = obj
        obj._clear()
        obj._data_status = DataStatus.NOT_SETUP
        obj._executable_finder = ExecutableFinder()
        obj._reset_status = ResetStatus.NOT_SETUP
        obj._run_status = RunStatus.NOT_SETUP

        return obj

    def _clear(self):
        """
        Clears out all data
        """
        self._run_dir_path = None
        self._temporary_directory = None
        self._hard_reset()

    def _hard_reset(self):
        """
        Puts all data back into the state expected at graph changed and
            sim.reset
        """
        self._run_dir_path = None
        self._soft_reset()

    def _soft_reset(self):
        """
        Puts all data back into the state expected at sim.reset but not
        graph changed

        """
        # Holder for any future values


class UtilsDataView(object):
    """
    A read only view of the data available at FEC level

    The objects accessed this way should not be changed or added to.
    Changing or adding to any object accessed if unsupported as bypasses any
    check or updates done in the writer(s).
    Objects returned could be changed to immutable versions without notice!

    All methods are class methods so can be accessed directly

    The get_ methods will either return a valid value or
    raise an Exception if the data is currently not available.
    The get methods will will not return None unless specifically documented
    to do so.
    As a reasonable effort is made the setters to verify the data types,
    the get methods can be expected to return the correct type.

    The iterate_ methods offer a view over the items in a mutible data object.
    There is no guarantee if the returned iterator will nor will not reflect
    any changes to the underlying data object,
    nor that how a method behaves in this way does not change over time.
    So the methods should be called for every iteration.

    add_ methods allow for the scripts directly or indirectly to add extra
    values.
    They allow the view to add extra safetly such as type checking.
    They will raise an exception if called while the simulator is running.

    The has_ methods will return True is the value is known and False if not.
    Semantically the are the same as checking if the get returns a None.
    They may be faster if the object needs to be generated on the fly or
    protected to be made immutable.
    Has methods have been added where needed.
    More can easily be added if required.

    The is_ methods will return a bool value to say teh simulator is in
    the expected state.
    They may throw an exception if called at an unexpected time.
    For example if called before sim.setup or after sim.end

    While how and where the underpinning DataModel(s) store data can change
    without notice, methods in this class can be considered a supported API
    """

    __data = _UtilsDataModel()
    __slots__ = []

    @classmethod
    def _exception(cls, data):
        """
        The most suitable no data Exception based on the status

        :param str data: Name of the data not found
        :rtype: ~spinn_utilities.exceptions.SpiNNUtilsException
        """
        return cls.__data._data_status.exception(data)

    # Report directories
    # There are NO has or get methods for directories
    # This allow directories to be created on the fly
    # Remainder in FecDataView

    @classmethod
    def _temporary_dir_path(cls):
        """
        The path to an existing temp directory

        :param str data: Name of the data to be replace with temp
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            if not in Mocked state
        """
        if cls.__data._temporary_directory is None:
            cls.__data._temporary_directory = tempfile.TemporaryDirectory()
        return cls.__data._temporary_directory.name

    # Status checks

    @classmethod
    def _is_mocked(cls):
        """
        Checks if the view is in mocked state

        :rtype: bool
        """
        return cls.__data._data_status == DataStatus.MOCKED

    @classmethod
    def is_hard_reset(cls):
        """
        Check if the system has been hard reset since the last run finished.

        Critically during the first run after reset this continues to return
        True!

        Returns False after a reset that was considered soft.

        :rtype: bool
        """
        return cls.__data._reset_status == ResetStatus.HARD_RESET

    @classmethod
    def is_soft_reset(cls):
        """
        Check if the system has been soft_reset since the last run finished.

        Critically during the first run after reset this continues to return
        True!

        Returns False after a reset that was considered soft.

        :rtype: bool
        """
        return cls.__data._reset_status == ResetStatus.SOFT_RESET

    @classmethod
    def is_ran_ever(cls):
        """
        Check if the simulation has run at least once, ignoring resets

        :rtype: bool
        :raises NotImplementedError:
            If this is called from an unexpected state
        """
        if cls.__data._reset_status == ResetStatus.SETUP:
            return False
        if cls.__data._reset_status in [
                ResetStatus.HAS_RUN, ResetStatus.SOFT_RESET,
                ResetStatus.HARD_RESET]:
            return True
        raise NotImplementedError(
            f"This call was not expected with reset status "
            f"{cls.__data._reset_status}")

    @classmethod
    def is_ran_last(cls):
        """
        Checks if the simulation has run and not been reset.

        :rytpe: bool
        """
        if cls.__data._reset_status == ResetStatus.HAS_RUN:
            return True
        if cls.__data._reset_status in [
                ResetStatus.SETUP, ResetStatus.SOFT_RESET,
                ResetStatus.HARD_RESET]:
            return False
        raise NotImplementedError(
            f"This call was not expected with reset status "
            f"{cls.__data._reset_status}")

    @classmethod
    def is_no_stop_requested(cls):
        """
        Checks that a stop request has not been sent

        :return:
        """
        if cls.__data._run_status == RunStatus.IN_RUN:
            return True
        if cls.__data._run_status == RunStatus.STOP_REQUESTED:
            return False
        raise NotImplementedError(
            f"This call was not expected with run status "
            f"{cls.__data._run_status}")

    @classmethod
    def is_running(cls):
        """
        Checks if there is currently a simulaation running

        That is a call to run has started but not yet stopped,

        :rtype: bool
        """
        return cls.__data._run_status in [
            RunStatus.IN_RUN, RunStatus.STOP_REQUESTED]

    @classmethod
    def check_valid_simulator(cls):
        """
        Throws an error if there is no simulator

        :raises SimulatorNotSetupException: If called before sim.setup
        :raises SimulatorShutdownException: If called after sim.end
        """
        if cls.__data._run_status in [
                RunStatus.NOT_RUNNING, RunStatus.IN_RUN,
                RunStatus.STOP_REQUESTED, RunStatus.STOPPING]:
            return
        if cls.__data._run_status == RunStatus.NOT_SETUP:
            raise SimulatorNotSetupException(
                "This call is not supported before setup has been called")
        if cls.__data._run_status == RunStatus.SHUTDOWN:
            raise SimulatorShutdownException(
                "This call is not valid after end or stop has been called")
        raise NotImplementedError(
            f"Unexpected run state: {cls.__data._run_status}")

    @classmethod
    def check_user_can_act(cls):
        """
        Checks if the status is such that users can be making calls

        :raises SimulatorRunningException: If sim.run is currently running
        :raises SimulatorNotSetupException: If called before sim.setup
        :raises SimulatorShutdownException: If called after sim.end
        """
        if cls.__data._run_status == RunStatus.NOT_RUNNING:
            return
        if cls.__data._data_status == DataStatus.MOCKED:
            return
        if cls.__data._run_status in [
                RunStatus.IN_RUN, RunStatus.STOPPING,
                RunStatus.STOP_REQUESTED]:
            raise SimulatorRunningException(
                f"This call is not supported while the simulator is running "
                f"and in state {cls.__data._run_status}")
        cls.check_valid_simulator()

    @classmethod
    def is_setup(cls):
        """
        Checks to see if there is already a simulator

        :rtype: bool
        """
        if cls.__data._run_status in [RunStatus.NOT_SETUP, RunStatus.SHUTDOWN]:
            return False
        if cls.__data._run_status in [
                RunStatus.NOT_RUNNING, RunStatus.IN_RUN,
                RunStatus.STOP_REQUESTED, RunStatus.STOPPING]:
            return True
        raise NotImplementedError(
            f"This call was not expected with run status "
            f"{cls.__data._run_status}")

    @classmethod
    def is_user_mode(cls):
        """
        Determines if simulator is currently not running so user is\
        accessing data

        This returns False in the Mocked state

        :rtpye: bool
        :raises NotImplementedError: If the data has not yet been settup or
            on an unexpected run_status
        """
        if cls.__data._run_status in [
                RunStatus.IN_RUN, RunStatus.STOPPING,
                RunStatus.STOP_REQUESTED]:
            return False
        if cls.__data._run_status in [
                RunStatus.NOT_RUNNING, RunStatus.SHUTDOWN]:
            return True
        if cls._is_mocked():
            return False
        raise NotImplementedError(
            f"Unexpected with RunStatus {cls.__data._run_status}")

    @classmethod
    def is_stop_already_requested(cls):
        """
        Checks if there has already been a request stop

        Also checks the state is such that a stop request makes sense.

        :return: True if the stop has already been requested
            or if the system is stopping or has already stopped
            False if the stop request makes sense.
        :raises SpiNNUtilsException:
            If the stop_run was not expected in the current state.
        """
        if cls.__data._run_status == RunStatus.IN_RUN:
            return False
        if cls.__data._run_status == RunStatus.STOP_REQUESTED:
            return True
        cls.check_valid_simulator()
        if cls.is_ran_ever():
            raise UnexpectedStateChange(
                "Calling stop after run has finished does not make sense")
        raise UnexpectedStateChange(
                "Calling stop before run does not make sense")

    @classmethod
    def get_run_dir_path(cls):
        """
        Returns the path to the directory that holds all the reports for run

        This will be the path used by the last run call or to be used by
        the next run if it has not yet been called.

        ..note: In unittest mode this returns a tempdir
        shared by all path methods

        :rtpye: str
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the run_dir_path is currently unavailable
        """
        if cls.__data._run_dir_path:
            return cls.__data._run_dir_path
        if cls._is_mocked():
            return cls._temporary_dir_path()
        raise cls._exception("run_dir_path")

    @classmethod
    def get_executable_finder(cls):
        """
        The ExcutableFinder object created at time code is imported

        :rtype: ExcutableFinder
        """
        return cls.__data._executable_finder
