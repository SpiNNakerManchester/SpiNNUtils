# Copyright (c) 2019-2020 The University of Manchester
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


class SpiNNUtilsException(Exception):
    """ Superclass of all exceptions from the SpiNNUtils module.
    """


class UnexpectedStateChange(SpiNNUtilsException):
    """
    raise when trying to change the state in an unexpected way
    """


class NotSetupException(SpiNNUtilsException):
    """
    Raised when trying to get data before simulator has been setup
    """

    def __init__(self, data):
        super().__init__(f"Requesting {data} is not valid before setup")


class InvalidDirectory(SpiNNUtilsException):
    """
    Raise when trying to set an invalid Directory
    """
    def __init__(self, name, value):
        super().__init__(f"Unable to set {name} has {value} is not a dir.")


class DataNotYetAvialable(SpiNNUtilsException):
    """
    Raised when trying to get data before simulator has created it
    """
    def __init__(self, data):
        super().__init__(f"{data} has not yet been created.")


class DataChanged(SpiNNUtilsException):
    """
    Raised when trying to get data after some changed
    """
    def __init__(self, data):
        super().__init__(f"{data} has been changed.")


class DataNotMocked(DataNotYetAvialable):
    """
    Raised when trying to get data before a mocked simulator has created it
    """
    def __init__(self, data):
        super().__init__(f"MOCK {data}")


class IllegalState(DataNotYetAvialable):
    """
    Raised when trying to get data before a mocked simulator has created it
    """


class ShutdownException(SpiNNUtilsException):
    """
    Raised when trying to get simulator data after it has been shut down
    """
    def __init__(self, data):
        super().__init__(f"Requesting {data} is not valid after end")


class IllegalWriterException(SpiNNUtilsException):
    """
    Raised when trying to create a writer other than setup or Mock
    """


class SimulatorNotSetupException(SpiNNUtilsException):
    """
    Raised when trying to get simulator before it has been setup
    """


class SimulatorShutdownException(SpiNNUtilsException):
    """
    Raised when trying to get simulator after it has been shit down
    """


class SimulatorRunningException(SpiNNUtilsException):
    """
    Raised when trying an action that should not happen while the simulator
    is running
    """


class SimulatorNotRunException(SpiNNUtilsException):
    """
    Raised when trying to reset or stop before starting
    """


class ConfigException(SpiNNUtilsException):
    """
    Raise when reading or setting configs went wrong
    """


class UnexpectedCException(SpiNNUtilsException):
    """
    Raise when the Converted which replaces log messages found a pattern
    it did not expect and can not handle
    """
