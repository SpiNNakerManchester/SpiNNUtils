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

import tempfile
from .data_status import DataStatus
from .reset_status import ResetStatus
from .run_status import RunStatus
from spinn_utilities.exceptions import (
    SimulatorNotSetupException, SimulatorRunningException,
    SimulatorShutdownException, UnexpectedStateChange)
from spinn_utilities.executable_finder import ExecutableFinder
# pylint: disable=protected-access


class _UtilsDataModel(object):
    """
    Singleton data model.

    This class should not be accessed directly please use the DataView and
    DataWriter classes.
    Accessing or editing the data held here directly is *not supported!*

    There may be other DataModel classes which sit next to this one and hold
    additional data. The DataView and DataWriter classes will combine these
    as needed.

    What data is held where and how can change without notice.
    """

    __singleton = None

    __slots__ = [
        "_data_status",
        "_executable_finder",
        "_report_dir_path",
        "_requires_data_generation",
        "_requires_mapping",
        "_reset_status",
        "_run_dir_path",
        "_run_status",
        "_temporary_directory",
    ]

    def __new__(cls):
        if cls.__singleton:
            return cls.__singleton
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
        Clears out all data.
        """
        self._report_dir_path = None
        self._hard_reset()

    def _hard_reset(self):
        """
        Puts all data back into the state expected at graph changed and
        `sim.reset`.
        """
        self._run_dir_path = None
        self._requires_data_generation = True
        self._requires_mapping = True
        self._temporary_directory = None
        self._soft_reset()

    def _soft_reset(self):
        """
        Puts all data back into the state expected at `sim.reset` but not
        graph changed.
        """
        # Holder for any future values


class UtilsDataView(object):
    """
    A read only view of the data available at each level.

    .. note::
        The state model of this class is designed primarily to support
        sPyNNaker.

    All methods are class methods so can be accessed directly without
    instantiating a view.
    There is a stack of subclasses such as `MachineDataView`, `FecDataView`,
    `SpynnakerDataView` (and more). All inherit all methods.
    We reserve the right to override methods defined in one View in subclasses.

    There are also Writer classes which override the Views but these are
    specifically designed to only be usable in unit tests and by the simulator
    (ASB) directly.

    You should use the data view most appropriate to what you are doing i.e.
    If you are accessing it from a class or function in FEC,
    use `FecDataView` but if you are accessing it from sPyNNaker,
    use `SpynnakerDataView`.
    This will ensure that any changes to the view local to the code will
    affect all code in that package

    The objects accessed this way should not be changed or added to.
    Changing or adding to any object accessed is unsupported as bypasses any
    check or updates done in the writer(s).
    Objects returned could be changed to immutable versions without notice!

    The `get...` methods will either return a valid value or
    raise an exception if the data is currently not available.
    The `get` methods will will not return `None` unless specifically
    documented to do so.
    As a reasonable effort is made the setters to verify the data types,
    the get methods can be expected to return the correct type.

    There are also several semantic sugar `get...` methods.
    Some are slightly faster but many are just to make the code more readable.
    Some semantic sugar methods do not start with get to keep the same name as
    the existing function on the object has.

    The `iterate...` methods offer a view over the collections within
    mutable data objects, particularly ones changed between runs.
    There is no guarantee if the returned iterator will or will not reflect
    any changes to the underlying data object,
    nor that how a method behaves in this way does not change over time.
    So the methods should be called for every iteration.

    Each `iterate...` method will have a corresponding `get_n...` which you
    need to do instead of `len(iterate...)` as we reserve the right to make
    any `iterate...` method return an iterable which does not support `len`
    without notice.

    `add...` methods allow for the scripts directly or indirectly to add extra
    values.
    They allow the view to add extra safety such as type checking.
    They will raise an exception if called while the simulator is running.

    The `has...` methods will return True if the value is known and False if
    not.
    Semantically they are the same as checking if the get raises an exception.
    They may be faster if the object needs to be generated on the fly or
    protected to be made immutable.
    `has...` methods have been added where found needed.
    More can easily be added if required.

    The `is...` methods will return a boolean value to say the simulator is in
    the expected state.
    They may throw an exception if called at an unexpected time.
    For example if called before `sim.setup` or after `sim.end`.

    While how and where the underpinning DataModel(s) store data can change
    without notice, methods in View classes can be considered a supported API.
    """

    __data = _UtilsDataModel()
    __slots__ = []

    @classmethod
    def _exception(cls, data):
        """
        The most suitable no data Exception based on the status.

        :param str data: Name of the data not found
        :rtype: ~spinn_utilities.exceptions.SpiNNUtilsException
        """
        return cls.__data._data_status.exception(data)

    # Status checks

    @classmethod
    def _is_mocked(cls):
        """
        Checks if the view is in mocked state.

        :rtype: bool
        """
        return cls.__data._data_status == DataStatus.MOCKED

    @classmethod
    def is_hard_reset(cls):
        """
        Check if the system has been hard reset since the last run
        *finished*.

        .. warning::
            During the first run after reset this continues to return True!

        Returns False after a reset that was considered soft.

        :rtype: bool
        """
        return cls.__data._reset_status == ResetStatus.HARD_RESET

    @classmethod
    def is_soft_reset(cls):
        """
        Check if the system has been soft reset since the last run *finished*.

        .. warning::
            During the first run after reset this continues to return True!

        Returns False after a reset that was considered hard.

        :rtype: bool
        """
        return cls.__data._reset_status == ResetStatus.SOFT_RESET

    @classmethod
    def is_ran_ever(cls):
        """
        Check if the simulation has run at least once, ignoring resets.

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

        :rtype: bool
        :raises NotImplementedError:
            If this is called from an unexpected state
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
    def is_reset_last(cls):
        """
        Reports if `sim.reset` called since the last `sim.run`.

        Unlike :py:meth:`is_soft_reset` and :py:meth:`is_hard_reset` this
        method return False during any `sim.run`.

        It also returns False after a `sim.stop` or `sim.end` call starts

        :rtype: bool
        :raises NotImplementedError:
            If this is called from an unexpected state
        """
        if cls.__data._reset_status in [
                ResetStatus.SETUP, ResetStatus.HAS_RUN]:
            return False
        if cls.__data._reset_status in [
                ResetStatus.SOFT_RESET, ResetStatus.HARD_RESET]:
            if cls.__data._run_status == RunStatus.NOT_RUNNING:
                return True
            if cls.__data._run_status == RunStatus.IN_RUN:
                return False
        if cls.__data._run_status in [
                RunStatus.STOP_REQUESTED, RunStatus.STOPPING,
                RunStatus.SHUTDOWN]:
            raise SimulatorShutdownException(
                "This call is not supported after sim.stop/end or "
                "sim.end has been called")
        raise NotImplementedError(
            f"This call was not expected with reset status "
            f"{cls.__data._reset_status} and run status "
            f"{cls.__data._run_status}")

    @classmethod
    def is_no_stop_requested(cls):
        """
        Checks that a stop request has not been sent.

        :rtype: bool
        :raises NotImplementedError:
            If this is called from an unexpected state
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
        Checks if there is currently a simulation running.

        That is a call to run has started but not yet stopped.

        :rtype: bool
        """
        return cls.__data._run_status in [
            RunStatus.IN_RUN, RunStatus.STOP_REQUESTED]

    @classmethod
    def check_valid_simulator(cls):
        """
        Throws an error if there is no simulator.

        :raises SimulatorNotSetupException: If called before `sim.setup`
        :raises SimulatorShutdownException: If called after `sim.end`
        """
        if cls.__data._run_status in [
                RunStatus.NOT_RUNNING, RunStatus.IN_RUN,
                RunStatus.STOP_REQUESTED, RunStatus.STOPPING]:
            return
        if cls.__data._data_status == DataStatus.MOCKED:
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
        Checks if the status is such that users can be making calls.

        This does *not* error in the Mocked state

        :raises SimulatorRunningException: If `sim.run` is currently running
        :raises SimulatorNotSetupException: If called before `sim.setup`
        :raises SimulatorShutdownException: If called after `sim.end`
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
        Checks to see if there is already a simulator.

        :rtype: bool
        :raises NotImplementedError:
            If this is called from an unexpected state
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
        Determines if simulator is currently not running so user is
        accessing data.

        This returns False in the Mocked state.

        :rtype: bool
        :raises NotImplementedError:
            If the data has not yet been set up or on an unexpected run_status
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
        Checks if there has already been a request stop.

        Also checks the state is such that a stop request makes sense.

        :return: True if the stop has already been requested
            or if the system is stopping or has already stopped
            False if the stop request makes sense.
        :rtype: bool
        :raises NotImplementedError:
            If this is called from an unexpected state
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
    def is_shutdown(cls):
        """
        Determines if simulator has already been shutdown.

        This returns False in the Mocked state

        :rtype: bool
        """
        return cls.__data._run_status == RunStatus.SHUTDOWN

    # Report directories
    # Remainder in FecDataView

    @classmethod
    def _temporary_dir_path(cls):
        """
        The path to an existing temporary directory, creating it if needed.

        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            if not in Mocked state
        """
        if cls.__data._temporary_directory is None:
            cls.__data._temporary_directory = tempfile.TemporaryDirectory()
        return cls.__data._temporary_directory.name

    @classmethod
    def get_run_dir_path(cls):
        """
        Returns the path to the directory that holds all the reports for run.

        This will be the path used by the last run call or to be used by
        the next run if it has not yet been called.

        .. note::
            In unit test mode this returns a temporary directory
            shared by all path methods.

        :rtype: str
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
        The ExcutableFinder object created at time code is imported.

        :rtype: ExcutableFinder
        """
        return cls.__data._executable_finder

    @classmethod
    def register_binary_search_path(cls, search_path):
        """
        Register an additional binary search path for executables.

        Syntactic sugar for `get_executable_finder().add_path()`

        :param str search_path: absolute search path for binaries
        """
        cls.__data._executable_finder.add_path(search_path)

    @classmethod
    def get_executable_path(cls, executable_name):
        """
        Finds an executable within the set of folders. The set of folders
        is searched sequentially and the first match is returned.

        Syntactic sugar for `get_executable_finder().get_executable_path()`

        :param str executable_name: The name of the executable to find
        :return: The full path of the discovered executable
        :rtype: str
        :raises KeyError: If no executable was found in the set of folders
        """
        return cls.__data._executable_finder.get_executable_path(
            executable_name)

    @classmethod
    def get_executable_paths(cls, executable_names):
        """
        Finds each executables within the set of folders.

        The names are assumed to be comma separated
        The set of folders is searched sequentially
        and the first match for each name is returned.

        Names not found are ignored and not added to the list.

        Syntactic sugar for `get_executable_finder().get_executable_paths()`

        :param str executable_names: The name of the executable to find.
            Assumed to be comma separated.
        :return:
            The full path of the discovered executable, or ``None`` if no
            executable was found in the set of folders
        :rtype: list(str)
        """
        return cls.__data._executable_finder.get_executable_paths(
            executable_names)

    @classmethod
    def get_requires_data_generation(cls):
        """
        Reports if data generation is required.

        Set to True at the start and by any change that could require
        data generation or mapping
        Remains True during the first run after a data change
        Only set to False at the *end* of the first run

        :rtype: bool
        """
        return cls.__data._requires_data_generation

    @classmethod
    def set_requires_data_generation(cls):
        """
        Sets `requires_data_generation` to True.

        Only the end of a run can set it to False
        """
        cls.check_user_can_act()
        cls.__data._requires_data_generation = True

    @classmethod
    def get_requires_mapping(cls):
        """
        Reports if mapping is required.

        Set to True at the start and by any change that could require
        any mapping stage to be called
        Remains True during the first run after a requires mapping.
        Only set to False at the *end* of the first run

        :rtype: bool
        """
        return cls.__data._requires_mapping

    @classmethod
    def set_requires_mapping(cls):
        """
        Sets `requires_mapping` and `requires_data_generation` to True.

        Only the end of a run can set it to False
        """
        cls.check_user_can_act()
        cls.__data._requires_mapping = True
        cls.__data._requires_data_generation = True

    @classmethod
    def _mock_has_run(cls):
        """
        Mock the status as if run has been called and finished!

        .. warning::

            *ONLY FOR USE IN UNITTESTS*

            Any use outside of unit tests is *not* supported and will cause
            errors!
        """
        cls.__data._run_status = RunStatus.NOT_RUNNING
        cls.__data._reset_status = ResetStatus.HAS_RUN
        cls.__data._requires_data_generation = False
        cls.__data._requires_mapping = False
