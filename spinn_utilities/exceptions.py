# Copyright (c) 2019 The University of Manchester
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


class SpiNNUtilsException(Exception):
    """
    Superclass of all exceptions from the SpiNNUtils module.
    """


class UnexpectedStateChange(SpiNNUtilsException):
    """
    Raised when trying to change the state in an unexpected way.
    """


class NotSetupException(SpiNNUtilsException):
    """
    Raised when trying to get data before simulator has been setup.
    """

    def __init__(self, data):
        super().__init__(f"Requesting {data} is not valid before setup")


class InvalidDirectory(SpiNNUtilsException):
    """
    Raised when trying to set an invalid directory.
    """
    def __init__(self, name, value):
        super().__init__(f"Unable to set {name} has {value} is not a dir.")


class DataNotYetAvialable(SpiNNUtilsException):
    """
    Raised when trying to get data before simulator has created it.
    """
    def __init__(self, data):
        super().__init__(f"{data} has not yet been created.")


class DataChanged(SpiNNUtilsException):
    """
    Raised when trying to get data after some changed.
    """
    def __init__(self, data):
        super().__init__(f"{data} has been changed.")


class DataNotMocked(DataNotYetAvialable):
    """
    Raised when trying to get data before a mocked simulator has created it.
    """
    def __init__(self, data):
        super().__init__(f"MOCK {data}")


class IllegalState(DataNotYetAvialable):
    """
    Raised when trying to get data before a mocked simulator has created it.
    """


class ShutdownException(SpiNNUtilsException):
    """
    Raised when trying to get simulator data after it has been shut down.
    """
    def __init__(self, data):
        super().__init__(f"Requesting {data} is not valid after end")


class IllegalWriterException(SpiNNUtilsException):
    """
    Raised when trying to create a writer other than setup or Mock.
    """


class SimulatorNotSetupException(SpiNNUtilsException):
    """
    Raised when trying to get simulator before it has been setup.
    """


class SimulatorShutdownException(SpiNNUtilsException):
    """
    Raised when trying to get simulator after it has been shut down.
    """


class SimulatorRunningException(SpiNNUtilsException):
    """
    Raised when trying an action that should not happen while the simulator
    is running.
    """


class SimulatorNotRunException(SpiNNUtilsException):
    """
    Raised when trying to reset or stop before starting.
    """


class ConfigException(SpiNNUtilsException):
    """
    Raised when reading or setting configurations went wrong.
    """


class UnexpectedCException(SpiNNUtilsException):
    """
    Raised when the converter (which replaces log messages) found a pattern
    it did not expect and cannot handle.
    """
