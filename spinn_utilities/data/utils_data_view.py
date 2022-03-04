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
from spinn_utilities.exceptions import DataLocked, DataNotMocked
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

    All methods are class methods so can be accessed dirrectly

    The methods will either return a valid value or
    raise an Exception if the data is currently not available.
    These are typically semantic sugar around the get methods.

    The has methods will return True is the value is known and False if not.
    Semantically the are the same as checking if the get returns a None.
    They may be faster if the object needs to be generated on the fly or
    protected to be made immutable.

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

    @classmethod
    def _is_mocked(cls):
        return cls.__data._data_status == DataStatus.MOCKED

    @classmethod
    def _is_in_run(cls):
        return cls.__data._data_status == DataStatus.MOCKED

    @classmethod
    def _check_user_write(cls):
        """
        Throws an erro if the status is such that users should not change data

        :raises DataLocked:
        """
        if cls.__data._run_status in [RunStatus.MOCKED, RunStatus.NOT_RUNNING]:
            return
        raise DataLocked(cls.__data._run_status)

    @classmethod
    def _is_running(cls):
        """
        Dettermines if simulator is currently running.

        This returns True in the Mocked state

        :rtpye: bool
        :raises NotImplementedError: If the data has not yet been settup or
            on an unexpected run_status
        """
        if cls.__data._run_status in [
                RunStatus.MOCKED, RunStatus.IN_RUN, RunStatus.STOPPING]:
            return True
        if cls.__data._run_status in [
                RunStatus.NOT_RUNNING, RunStatus.SHUTDOWN]:
            return False
        raise NotImplementedError(
            f"Unexpected with RunStatus {cls.__data._run_status}")

    @classmethod
    def _has_run(cls):
        """

        :return:
        """

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
