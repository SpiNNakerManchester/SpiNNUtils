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


class FailedToFindBinaryException():
    """ Raised when the executable finder cant find the binary
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
        super().__init__(f"MOCK {data} has not yet been created.")


class DataLocked(SpiNNUtilsException):
    """
    Raised when trying to access data while in a state it is locked
    """
    def __init__(self, data, state):
        super().__init__(f"Illegal call to get {data} while {state}.")


class IllegalState(DataNotYetAvialable):
    """
    Raised when trying to get data before a mocked simulator has created it
    """


class ShutdownException(SpiNNUtilsException):
    """
    Raised when trying to get simulator data after it has been shit down
    """
    def __init__(self, data):
        super().__init__(f"Requesting {data} is not valid after end")
