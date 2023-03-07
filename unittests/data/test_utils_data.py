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

import os
import unittest
from spinn_utilities.data import UtilsDataView
from spinn_utilities.data.reset_status import ResetStatus
from spinn_utilities.data.run_status import RunStatus
from spinn_utilities.data.utils_data_writer import UtilsDataWriter
from spinn_utilities.data.data_status import DataStatus
from spinn_utilities.config_setup import unittest_setup
from spinn_utilities.exceptions import (
    DataNotYetAvialable, IllegalWriterException, InvalidDirectory,
    NotSetupException,
    SimulatorNotRunException, SimulatorNotSetupException,
    SimulatorRunningException, SimulatorShutdownException,
    UnexpectedStateChange)


class TestUtilsData(unittest.TestCase):

    def setUp(cls):
        unittest_setup()

    def test_not_setup(self):
        # NOT_SETUP only reachable on first call or via hack
        UtilsDataWriter._UtilsDataWriter__data._data_status = \
            DataStatus.NOT_SETUP
        UtilsDataWriter._UtilsDataWriter__data._reset_status = \
            ResetStatus.NOT_SETUP
        UtilsDataWriter._UtilsDataWriter__data._run_status = \
            RunStatus.NOT_SETUP
        with self.assertRaises(NotSetupException):
            UtilsDataView.get_run_dir_path()

        self.assertFalse(UtilsDataView._is_mocked())
        with self.assertRaises(SimulatorNotSetupException):
            UtilsDataView.check_valid_simulator()
        with self.assertRaises(SimulatorNotSetupException):
            UtilsDataView.check_user_can_act()
        with self.assertRaises(NotImplementedError):
            self.assertFalse(UtilsDataView.is_user_mode())
        with self.assertRaises(SimulatorNotSetupException):
            UtilsDataView.is_stop_already_requested()
        self.assertFalse(UtilsDataView.is_shutdown())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_soft_reset())
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_ran_ever()
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_ran_last()
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_reset_last()
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertFalse(UtilsDataView.is_setup())
        # No writer yet so no way to call state change methods

    def test_mocked(self):
        writer = UtilsDataWriter.mock()

        self.assertTrue(UtilsDataView._is_mocked())
        # Most is tests return True if mocked
        UtilsDataView.check_user_can_act()
        UtilsDataView.check_valid_simulator()
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_stop_already_requested()
        self.assertFalse(UtilsDataView.is_shutdown())
        self.assertFalse(UtilsDataView.is_user_mode())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_soft_reset())
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_ran_ever()
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_ran_last()
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_reset_last()
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertFalse(UtilsDataView.is_setup())

        # No state change out of Mocked allowed except for setup of course
        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        with self.assertRaises(UnexpectedStateChange):
            writer.finish_run()
        with self.assertRaises(UnexpectedStateChange):
            # Should not be able to call
            writer.hard_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.soft_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        with self.assertRaises(UnexpectedStateChange):
            writer.stopping()
        # TODO do we need to block this?
        writer.shut_down()

    def test_setup(self):
        writer = UtilsDataWriter.setup()

        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView.is_user_mode())
        with self.assertRaises(UnexpectedStateChange):
            UtilsDataView.is_stop_already_requested()
        self.assertFalse(UtilsDataView.is_shutdown())
        UtilsDataView.check_valid_simulator()
        UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        self.assertFalse(UtilsDataView.is_reset_last())
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())

        # writer.start_run() see test_start
        with self.assertRaises(UnexpectedStateChange):
            writer.finish_run()
        with self.assertRaises(SimulatorNotRunException):
            writer.hard_reset()
        with self.assertRaises(SimulatorNotRunException):
            writer.soft_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        # writer.stopping() see test_stopping
        writer.shut_down()
        self.check_shut_down(writer)

    def check_shut_down(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView.is_user_mode())
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.is_stop_already_requested()
        self.assertTrue(UtilsDataView.is_shutdown())
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.check_valid_simulator()
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        self.assertFalse(UtilsDataView.is_reset_last())
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertFalse(UtilsDataView.is_setup())
        self.check_after_shutdown(writer)

    def check_after_shutdown(self, writer):
        writer.shut_down()
        with self.assertRaises(SimulatorShutdownException):
            writer.stopping()
        with self.assertRaises(SimulatorShutdownException):
            writer.start_run()
        with self.assertRaises(SimulatorShutdownException):
            writer.finish_run()
        with self.assertRaises(SimulatorShutdownException):
            writer.hard_reset()
        with self.assertRaises(SimulatorShutdownException):
            writer.soft_reset()
        with self.assertRaises(SimulatorShutdownException):
            writer.request_stop()

    def test_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.stopping()
        self.check_stopping(writer)

    def check_stopping(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        with self.assertRaises(UnexpectedStateChange):
            UtilsDataView.is_stop_already_requested()
        self.assertFalse(UtilsDataView.is_shutdown())
        UtilsDataView.check_valid_simulator()
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_soft_reset())
        # Only set at end of the current run
        self.assertFalse(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        self.assertFalse(UtilsDataView.is_reset_last())
        with self.assertRaises(NotImplementedError):
            self.assertTrue(UtilsDataView.is_no_stop_requested())
        self.assertFalse(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        with self.assertRaises(UnexpectedStateChange):
            writer.finish_run()
        with self.assertRaises(SimulatorRunningException):
            writer.hard_reset()
        with self.assertRaises(SimulatorRunningException):
            writer.soft_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        with self.assertRaises(UnexpectedStateChange):
            writer.stopping()
        writer.shut_down()
        self.check_shut_down(writer)

    def test_start(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()

        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        self.assertFalse(UtilsDataView.is_stop_already_requested())
        self.assertFalse(UtilsDataView.is_shutdown())
        UtilsDataView.check_valid_simulator()
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_soft_reset())
        # Only set at end of the current run
        self.assertFalse(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        self.assertFalse(UtilsDataView.is_reset_last())
        self.assertTrue(UtilsDataView.is_no_stop_requested())
        self.assertTrue(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        # writer.finish_run() test_start_finish
        with self.assertRaises(SimulatorNotRunException):
            writer.hard_reset()
        with self.assertRaises(SimulatorRunningException):
            writer.soft_reset()
        # writer.request_stop() test_start_request
        # writer.stopping() test_start_stopping
        writer.shut_down()
        self.check_shut_down(writer)

    def test_start_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.stopping()
        self.check_stopping(writer)

    def test_start_finish(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        self.check_start_finish(writer)

    def check_start_finish(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView.is_user_mode())
        with self.assertRaises(UnexpectedStateChange):
            UtilsDataView.is_stop_already_requested()
        self.assertFalse(UtilsDataView.is_shutdown())
        UtilsDataView.check_valid_simulator()
        UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())
        self.assertFalse(UtilsDataView.is_reset_last())
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        # writer.start_run() test_start_finish_start
        with self.assertRaises(UnexpectedStateChange):
            writer.finish_run()
        # writer.hard_reset() test_start_finish_hard
        # writer.soft_reset() test_start_finish_soft
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        # writer.stopping() test_start_finish_stopping
        writer.shut_down()
        self.check_start_finish_shut_down(writer)

    def check_start_finish_shut_down(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView.is_user_mode())
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.is_stop_already_requested()
        self.assertTrue(UtilsDataView.is_shutdown())
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.check_valid_simulator()
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())
        self.assertFalse(UtilsDataView.is_reset_last())
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertFalse(UtilsDataView.is_setup())

        self.check_after_shutdown(writer)

    def test_start_finish_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.stopping()
        self.check_start_finish_stopping(writer)

    def check_start_finish_stopping(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        with self.assertRaises(UnexpectedStateChange):
            UtilsDataView.is_stop_already_requested()
        self.assertFalse(UtilsDataView.is_shutdown())
        self.assertFalse(UtilsDataView.is_user_mode())
        UtilsDataView.check_valid_simulator()
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())
        self.assertFalse(UtilsDataView.is_reset_last())
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        with self.assertRaises(UnexpectedStateChange):
            writer.finish_run()
        with self.assertRaises(SimulatorRunningException):
            writer.hard_reset()
        with self.assertRaises(SimulatorRunningException):
            writer.soft_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        with self.assertRaises(UnexpectedStateChange):
            writer.stopping()
        writer.shut_down()
        self.check_start_finish_shut_down(writer)

    def test_start_finish_hard(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.hard_reset()
        self.check_start_finish_hard(writer)

    def check_start_finish_hard(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView.is_user_mode())
        with self.assertRaises(UnexpectedStateChange):
            UtilsDataView.is_stop_already_requested()
        self.assertFalse(UtilsDataView.is_shutdown())
        UtilsDataView.check_valid_simulator()
        UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertTrue(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        self.assertTrue(UtilsDataView.is_reset_last())
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        # writer.start_run() test_start_finish_hard_start
        with self.assertRaises(UnexpectedStateChange):
            writer.finish_run()
        with self.assertRaises(UnexpectedStateChange):
            writer.hard_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.soft_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        # writer.stopping() test_start_finish_hard_stopping
        writer.shut_down()
        self.check_start_finish_hard_shut_down(writer)

    def check_start_finish_hard_shut_down(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView.is_user_mode())
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.is_stop_already_requested()
        self.assertTrue(UtilsDataView.is_shutdown())
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.check_valid_simulator()
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertTrue(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.is_reset_last()
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertFalse(UtilsDataView.is_setup())

        self.check_after_shutdown(writer)

    def test_start_finish_hard_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.hard_reset()
        writer.stopping()
        self.check_start_finish_hard_stopping(writer)

    def check_start_finish_hard_stopping(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        with self.assertRaises(UnexpectedStateChange):
            UtilsDataView.is_stop_already_requested()
        self.assertFalse(UtilsDataView.is_shutdown())
        self.assertFalse(UtilsDataView.is_user_mode())
        UtilsDataView.check_valid_simulator()
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertTrue(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.is_reset_last()
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        with self.assertRaises(UnexpectedStateChange):
            writer.finish_run()
        with self.assertRaises(SimulatorRunningException):
            writer.hard_reset()
        with self.assertRaises(SimulatorRunningException):
            writer.soft_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        with self.assertRaises(UnexpectedStateChange):
            writer.stopping()
        writer.shut_down()
        self.check_start_finish_hard_shut_down(writer)

    def test_start_finish_hard_start(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.hard_reset()
        writer.start_run()
        self.check_start_finish_hard_start(writer)

    def check_start_finish_hard_start(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        self.assertFalse(UtilsDataView.is_stop_already_requested())
        self.assertFalse(UtilsDataView.is_shutdown())
        UtilsDataView.check_valid_simulator()
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertTrue(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        self.assertFalse(UtilsDataView.is_reset_last())
        self.assertTrue(UtilsDataView.is_no_stop_requested())
        self.assertTrue(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        # writer.finish_run() test_start_finish_hard_start_finish
        with self.assertRaises(UnexpectedStateChange):
            writer.hard_reset()
        with self.assertRaises(SimulatorRunningException):
            writer.soft_reset()
        # writer.request_stop() test_start_finish_hard_start_request
        # writer.stopping() test_start_finish_hard_start_stopping
        writer.shut_down()
        self.check_start_finish_hard_shut_down(writer)

    def test_start_finish_hard_start_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.hard_reset()
        writer.start_run()
        writer.stopping()
        self.check_start_finish_hard_stopping(writer)

    def test_start_finish_start_hard_finish(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.hard_reset()
        writer.start_run()
        writer.finish_run()
        self.check_start_finish(writer)

    def test_start_finish_hard_start_request(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.hard_reset()
        writer.start_run()
        writer.request_stop()
        self.check_start_finish_hard_start_request(writer)

    def check_start_finish_hard_start_request(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        self.assertTrue(UtilsDataView.is_stop_already_requested())
        self.assertFalse(UtilsDataView.is_shutdown())
        UtilsDataView.check_valid_simulator()
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertTrue(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.is_reset_last()
        self.assertFalse(UtilsDataView.is_no_stop_requested())
        self.assertTrue(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        # writer.finish_run() test_start_finish_hard_start_request_finish
        with self.assertRaises(UnexpectedStateChange):
            writer.hard_reset()
        with self.assertRaises(SimulatorRunningException):
            writer.soft_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        # writer.stopping() test_start_finish_hard_start_request_stopping
        writer.shut_down()
        self.check_start_finish_hard_shut_down(writer)

    def test_start_finish_hard_start_request_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.hard_reset()
        writer.start_run()
        writer.request_stop()
        writer.stopping()
        self.check_start_finish_hard_stopping(writer)

    def test_start_finish_hard_start_request_finish(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.hard_reset()
        writer.start_run()
        writer.request_stop()
        writer.finish_run()
        self.check_start_finish(writer)

    def test_start_finish_start(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.start_run()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        self.assertFalse(UtilsDataView.is_stop_already_requested())
        self.assertFalse(UtilsDataView.is_shutdown())
        UtilsDataView.check_valid_simulator()
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())
        self.assertFalse(UtilsDataView.is_reset_last())
        self.assertTrue(UtilsDataView.is_no_stop_requested())
        self.assertTrue(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        # writer.finish_run() test_start_finish_start_finish
        # writer.hard_reset() test_start_finish_start_hard
        with self.assertRaises(SimulatorRunningException):
            writer.soft_reset()
        # writer.request_stop() test_start_finish_start_request
        # writer.stopping() test_start_finish_start_stopping
        writer.shut_down()
        self.check_start_finish_shut_down(writer)

    def test_start_finish_start_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.start_run()
        writer.stopping()
        self.check_start_finish_stopping(writer)

    def test_start_finish_start_finish(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.start_run()
        writer.finish_run()
        self.check_start_finish(writer)

    def test_start_finish_start_hard(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.start_run()
        writer.hard_reset()
        self.check_start_finish_hard_start(writer)

    def test_start_finish_start_request(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.start_run()
        writer.request_stop()

        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        self.assertTrue(UtilsDataView.is_stop_already_requested())
        self.assertFalse(UtilsDataView.is_shutdown())
        UtilsDataView.check_valid_simulator()
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())
        self.assertFalse(UtilsDataView.is_reset_last())
        self.assertFalse(UtilsDataView.is_reset_last())
        self.assertFalse(UtilsDataView.is_no_stop_requested())
        self.assertTrue(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        # writer.finish_run() test_start_finish_start_request_finish
        # writer.hard_reset()  test_start_finish_start_request_hard
        with self.assertRaises(SimulatorRunningException):
            writer.soft_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        # writer.stopping() test_start_finish_start_request_stopping
        writer.shut_down()
        self.check_start_finish_shut_down(writer)

    def test_start_finish_start_request_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.start_run()
        writer.request_stop()
        writer.stopping()
        self.check_start_finish_stopping(writer)

    def test_start_finish_start_request_hard(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.start_run()
        writer.request_stop()
        writer.hard_reset()
        self.check_start_finish_hard_start_request(writer)

    def test_start_finish_start_request_finish(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.start_run()
        writer.request_stop()
        writer.finish_run()
        self.check_start_finish(writer)

    def test_start_finish_soft(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView.is_user_mode())
        with self.assertRaises(UnexpectedStateChange):
            UtilsDataView.is_stop_already_requested()
        self.assertFalse(UtilsDataView.is_shutdown())
        UtilsDataView.check_valid_simulator()
        UtilsDataView.check_user_can_act()
        self.assertTrue(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        self.assertTrue(UtilsDataView.is_reset_last())
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        # writer.start_run() test_start_finish_soft_start
        with self.assertRaises(UnexpectedStateChange):
            writer.finish_run()
        # writer.hard_reset() test_start_finish_soft_hard
        with self.assertRaises(UnexpectedStateChange):
            writer.soft_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        # writer.stopping() test_start_finish_soft_stopping
        writer.shut_down()
        self.check_start_finish_soft_shutdown(writer)

    def check_start_finish_soft_shutdown(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView.is_user_mode())
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.is_stop_already_requested()
        self.assertTrue(UtilsDataView.is_shutdown())
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.check_valid_simulator()
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.check_user_can_act()
        self.assertTrue(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.is_reset_last()
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertFalse(UtilsDataView.is_setup())

        self.check_after_shutdown(writer)

    def test_start_finish_soft_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        writer.stopping()
        self.check_start_finish_start_soft_stopping(writer)

    def check_start_finish_start_soft_stopping(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        with self.assertRaises(UnexpectedStateChange):
            UtilsDataView.is_stop_already_requested()
        self.assertFalse(UtilsDataView.is_shutdown())
        self.assertFalse(UtilsDataView.is_user_mode())
        UtilsDataView.check_valid_simulator()
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertTrue(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.is_reset_last()
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        with self.assertRaises(UnexpectedStateChange):
            writer.finish_run()
        with self.assertRaises(SimulatorRunningException):
            writer.hard_reset()
        with self.assertRaises(SimulatorRunningException):
            writer.soft_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        with self.assertRaises(UnexpectedStateChange):
            writer.stopping()
        writer.shut_down()
        self.check_start_finish_soft_shutdown(writer)

    def test_start_finish_soft_hard(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        writer.hard_reset()
        self.check_start_finish_hard(writer)

    def test_start_finish_soft_start(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        writer.start_run()

        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        self.assertFalse(UtilsDataView.is_stop_already_requested())
        self.assertFalse(UtilsDataView.is_shutdown())
        UtilsDataView.check_valid_simulator()
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_soft_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        self.assertFalse(UtilsDataView.is_reset_last())
        self.assertTrue(UtilsDataView.is_no_stop_requested())
        self.assertTrue(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        # writer.finish_run() test_start_finish_soft_start_finsih
        # writer.hard_reset() test_start_finish_soft_start_hard
        with self.assertRaises(SimulatorRunningException):
            writer.soft_reset()
        # writer.request_stop() test_start_finish_soft_start_request
        # writer.stopping() test_start_finish_soft_start_stopping
        writer.shut_down()
        self.check_start_finish_soft_shutdown(writer)

    def test_start_finish_soft_start_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        writer.start_run()
        writer.stopping()
        self.check_start_finish_start_soft_stopping(writer)

    def test_start_finish_soft_start_hard(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        writer.start_run()
        writer.hard_reset()
        self.check_start_finish_hard_start(writer)

    def test_start_finish_soft_start_finish(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        writer.start_run()
        writer.finish_run()
        self.check_start_finish(writer)

    def test_start_finish_soft_start_request(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        writer.start_run()
        writer.request_stop()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        self.assertTrue(UtilsDataView.is_stop_already_requested())
        self.assertFalse(UtilsDataView.is_shutdown())
        UtilsDataView.check_valid_simulator()
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertTrue(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.is_reset_last()
        self.assertFalse(UtilsDataView.is_no_stop_requested())
        self.assertTrue(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        # writer.finish_run() test_start_finish_soft_start_request_finish
        # writer.hard_reset() test_start_finish_soft_start_request_hard
        with self.assertRaises(SimulatorRunningException):
            writer.soft_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        # writer.stopping() test_start_finish_soft_start_request_stopping
        writer.shut_down()
        self.check_start_finish_soft_shutdown(writer)

    def test_start_finish_soft_start_request_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        writer.start_run()
        writer.request_stop()
        writer.stopping()
        self.check_start_finish_start_soft_stopping(writer)

    def test_start_finish_soft_start_request_hard(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        writer.start_run()
        writer.request_stop()
        writer.hard_reset()
        self.check_start_finish_hard_start_request(writer)

    def test_start_finish_soft_start_request_finish(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        writer.start_run()
        writer.request_stop()
        writer.finish_run()
        self.check_start_finish(writer)

    def test_start_request(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.request_stop()

        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        self.assertTrue(UtilsDataView.is_stop_already_requested())
        self.assertFalse(UtilsDataView.is_shutdown())
        UtilsDataView.check_valid_simulator()
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_soft_reset())
        # Only set at end of the current run
        self.assertFalse(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        self.assertFalse(UtilsDataView.is_no_stop_requested())
        self.assertTrue(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        # writer.finish_run() test_start_request_finish
        with self.assertRaises(SimulatorNotRunException):
            writer.hard_reset()
        with self.assertRaises(SimulatorRunningException):
            writer.soft_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        # writer.stopping() test_start_request_finish_stopping
        writer.shut_down()
        self.check_shut_down(writer)

    def test_start_request_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.request_stop()
        writer.stopping()
        self.check_stopping(writer)

    def test_start_request_finish(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.request_stop()
        writer.finish_run()
        self.check_start_finish(writer)

    def test_directories_setup(self):
        writer = UtilsDataWriter.setup()
        # setup should clear mocked
        writer.setup()
        with self.assertRaises(DataNotYetAvialable):
            UtilsDataView.get_run_dir_path()

    def test_directories_mocked(self):
        UtilsDataWriter.mock()
        self.assertTrue(os.path.exists(UtilsDataView.get_run_dir_path()))

    def test_set_run_dir_path(self):
        writer = UtilsDataWriter.setup()
        writer.setup()
        with self.assertRaises(InvalidDirectory):
            writer.set_run_dir_path("bacon")
        writer.set_run_dir_path(os.path.curdir)
        self.assertEqual(os.path.curdir, UtilsDataView.get_run_dir_path())

    def test_set_report_dir_path(self):
        writer = UtilsDataWriter.setup()
        writer.setup()
        with self.assertRaises(InvalidDirectory):
            writer.set_report_dir_path("bacon")
        writer.set_report_dir_path(os.path.curdir)
        self.assertEqual(os.path.curdir, writer.get_report_dir_path())

    def test_writer_init_block(self):
        with self.assertRaises(IllegalWriterException):
            UtilsDataWriter(DataStatus.NOT_SETUP)
        with self.assertRaises(IllegalWriterException):
            UtilsDataWriter("bacon")

    def test_excutable_finder(self):
        writer = UtilsDataWriter.setup()
        ef = UtilsDataView.get_executable_finder()
        writer.start_run()
        writer.finish_run()
        writer.hard_reset()
        self.assertEqual(ef, UtilsDataView.get_executable_finder())
        UtilsDataWriter.setup()
        self.assertEqual(ef, UtilsDataView.get_executable_finder())

    def test_requires(self):
        writer = UtilsDataWriter.setup()
        # True before run
        self.assertTrue(writer.get_requires_data_generation())
        self.assertTrue(writer.get_requires_mapping())

        writer.start_run()
        # True during first run
        self.assertTrue(writer.get_requires_data_generation())
        self.assertTrue(writer.get_requires_mapping())
        # Can not be changed during run
        with self.assertRaises(SimulatorRunningException):
            writer.set_requires_data_generation()
        with self.assertRaises(SimulatorRunningException):
            writer.set_requires_mapping()
        writer.finish_run()

        # False after run
        self.assertFalse(writer.get_requires_data_generation())
        self.assertFalse(writer.get_requires_mapping())

        # Setting requires mapping sets both to True
        writer.set_requires_mapping()
        self.assertTrue(writer.get_requires_data_generation())
        self.assertTrue(writer.get_requires_mapping())

        writer.start_run()
        writer.finish_run()

        # Setting data only sets data
        writer.set_requires_data_generation()
        self.assertTrue(writer.get_requires_data_generation())
        self.assertFalse(writer.get_requires_mapping())

        writer.set_requires_mapping()
        self.assertTrue(writer.get_requires_data_generation())
        self.assertTrue(writer.get_requires_mapping())
