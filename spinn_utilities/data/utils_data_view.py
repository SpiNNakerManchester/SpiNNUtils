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

import tempfile
from .data_status import Data_Status


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
        # Data values cached
        "_run_dir_path",
        "_temporary_directory",
        # Data status mainly to raise best Exception
        "_status"
    ]

    def __new__(cls):
        if cls.__singleton:
            return cls.__singleton
        # pylint: disable=protected-access
        obj = object.__new__(cls)
        cls.__singleton = obj
        obj._clear()
        obj._status = Data_Status.NOT_SETUP
        return obj

    def _clear(self):
        """
        Clears out all data
        """
        self._temporary_directory = None
        self._hard_reset()

    def _hard_reset(self):
        """
        Puts all data back into the state expected at graph changed and
            sim.reset
        """
        self._run_dir_path = None

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

    The get methods will return either the value if known or a None.
    This is the faster way to access the data but lacks the safety.

    The property methods will either return a valid value or
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

    def _exception(self, data):
        """
        The most suitable no data Exception based on the status

        :param str data: Name of the data not found
        :rtype: ~spinn_utilities.exceptions.SpiNNUtilsException
        """
        return self.__data._status.exception(data)

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

    @property
    def status(self):
        """
        Returns the currentl status

        :rtype: Data_Status
        """
        return self.__data._status

    @classmethod
    def get_status(cls):
        """
        Returns the currentl status

        :rtype: Data_Status
        """
        return cls.__data._status

    @property
    def run_dir_path(self):
        """
        Returns the path to the directory that holds all the reports for run

        This will be the path used by the last run call or to be used by
        the next run if it has not yet been called.

        ..note: In unittest mode this returns a tempdir
        shared by all path methods

        :rtpye: str
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the simulation_time_step is currently unavailable
        """
        if self.__data._run_dir_path:
            return self.__data._run_dir_path

        if self.__data._status == Data_Status.MOCKED:
            return self._temporary_dir_path()

        raise self._exception("run_dir_path")

    @classmethod
    def get_run_dir_path(cls):
        """
        Returns the path to the directory that holds all the reports for run

        This will be the path used by the last run call or to be used by
        the next run if it has not yet been called.

        This call may return None if not yet set.

        ..note: In unittest mode this returns a tempdir
        shared by all path methods

        :rtpye: str
        """
        if cls.__data._status == Data_Status.MOCKED:
            return cls._temporary_dir_path()
        else:
            return cls.__data._run_dir_path
