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

        self.assertFalse(UtilsDataView._is_mocked())
        with self.assertRaises(SimulatorNotSetupException):
            UtilsDataView.check_user_can_act()
        with self.assertRaises(NotImplementedError):
            self.assertFalse(UtilsDataView.is_user_mode())
        with self.assertRaises(SimulatorNotSetupException):
            UtilsDataView.is_stop_already_requested()
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_soft_reset())
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_ran_ever()
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_ran_last()
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
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_stop_already_requested()
        self.assertFalse(UtilsDataView.is_user_mode())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_soft_reset())
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_ran_ever()
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_ran_last()
        with self.assertRaises(NotImplementedError):
             UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        with self.assertRaises(NotImplementedError):
            self.assertFalse(UtilsDataView.is_setup())

        # No state change out of Mocked allowed except for setup of course
        with self.assertRaises(NotImplementedError):
            writer.start_run()
        with self.assertRaises(UnexpectedStateChange):
            writer.finish_run()
        with self.assertRaises(NotImplementedError):
            # Should not be able to call
            writer.hard_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.soft_reset()
        with self.assertRaises(NotImplementedError):
            writer.request_stop()
        with self.assertRaises(NotImplementedError):
            writer.stopping()
        with self.assertRaises(UnexpectedStateChange):
            writer.shut_down()

    def test_setup(self):
        writer = UtilsDataWriter.setup()

        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView.is_user_mode())
        with self.assertRaises(UnexpectedStateChange):
            UtilsDataView.is_stop_already_requested()
        UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())

        # writer.start_run()
        with self.assertRaises(UnexpectedStateChange):
            writer.finish_run()
        with self.assertRaises(SimulatorNotRunException):
            writer.hard_reset()
        with self.assertRaises(SimulatorNotRunException):
            writer.soft_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        #writer.stopping()
        with self.assertRaises(UnexpectedStateChange):
            writer.shut_down()

    def test_start(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()

        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        self.assertFalse(UtilsDataView.is_stop_already_requested())
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_soft_reset())
        # Only set at end of the current run
        self.assertFalse(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        self.assertTrue(UtilsDataView.is_no_stop_requested())
        self.assertTrue(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        # writer.finish_run()
        with self.assertRaises(SimulatorNotRunException):
             writer.hard_reset()
        with self.assertRaises(SimulatorRunningException):
            writer.soft_reset()
        # writer.request_stop()
        # writer.stopping()
        with self.assertRaises(UnexpectedStateChange):
            writer.shut_down()

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
        UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())
        with self.assertRaises(NotImplementedError):
             UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        # writer.start_run()
        with self.assertRaises(UnexpectedStateChange):
            writer.finish_run()
        # writer.hard_reset() see test_status_hard_reset_after_run
        # writer.soft_reset() see test_status_soft_reset_after_run
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        # writer.stopping() test_status_stop_after_running
        with self.assertRaises(UnexpectedStateChange):
            writer.shut_down()

    def test_start_finish_start(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.start_run()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        self.assertFalse(UtilsDataView.is_stop_already_requested())
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())
        self.assertTrue(UtilsDataView.is_no_stop_requested())
        self.assertTrue(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        # writer.finish_run() # See test_status_finish_run2
        # writer.hard_reset() # see test_status_hard_reset_after_run2
        with self.assertRaises(SimulatorRunningException):
            writer.soft_reset()
        # writer.request_stop() # see test_status_request_stop_while_running2
        # writer.stopping()
        with self.assertRaises(UnexpectedStateChange):
            writer.shut_down()

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
        self.check_test_status_second_run_hard(writer)

    def check_test_status_second_run_hard(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        self.assertFalse(UtilsDataView.is_stop_already_requested())
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertTrue(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        self.assertTrue(UtilsDataView.is_no_stop_requested())
        self.assertTrue(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        # writer.finish_run()
        with self.assertRaises(UnexpectedStateChange):
            writer.hard_reset()
        with self.assertRaises(SimulatorRunningException):
            writer.soft_reset()
        # writer.request_stop()
        # writer.stopping()
        with self.assertRaises(UnexpectedStateChange):
            writer.shut_down()

    def test_start_finish_start_hard_finish(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.start_run()
        writer.hard_reset()
        writer.finish_run()
        self.check_start_finish(writer)

    def test_start_finish_start_hard_request(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.start_run()
        writer.hard_reset()
        writer.request_stop()
        self.check_start_hard_request(writer)

    def check_start_hard_request(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        self.assertTrue(UtilsDataView.is_stop_already_requested())
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertTrue(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        self.assertFalse(UtilsDataView.is_no_stop_requested())
        self.assertFalse(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        # writer.finish_run() see test_start_hard_request_finish
        with self.assertRaises(UnexpectedStateChange):
            writer.hard_reset()
        with self.assertRaises(SimulatorRunningException):
            writer.soft_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        # writer.stopping() ? test_status_stop_while_running
        with self.assertRaises(UnexpectedStateChange):
            writer.shut_down()

    def test_start_finish_start_hard_request_finish(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.start_run()
        writer.hard_reset()
        writer.request_stop()
        writer.finish_run()
        self.check_start_finish(writer)

    def test_start_finish_start_hard_request_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.start_run()
        writer.hard_reset()
        writer.request_stop()
        writer.stopping()
        self.check_stopping_after_hard(writer)

    def check_stopping_after_hard(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        with self.assertRaises(UnexpectedStateChange):
            UtilsDataView.is_stop_already_requested()
        self.assertFalse(UtilsDataView.is_user_mode())
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertTrue(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
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
        writer.stopping()
        writer.shut_down()

        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView.is_user_mode())
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.is_stop_already_requested()
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertTrue(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        with self.assertRaises(NotImplementedError):
             UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertFalse(UtilsDataView.is_setup())

        with self.assertRaises(SimulatorShutdownException):
            writer.start_run()
        with self.assertRaises(UnexpectedStateChange):
            writer.finish_run()
        with self.assertRaises(SimulatorShutdownException):
            writer.hard_reset()
        with self.assertRaises(SimulatorShutdownException):
            writer.soft_reset()
        with self.assertRaises(SimulatorShutdownException):
            writer.request_stop()
        with self.assertRaises(SimulatorShutdownException):
            writer.stopping()

    def test_start_finish_start_hard_request_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.start_run()
        writer.hard_reset()
        writer.stopping()
        self.check_stopping_after_hard(writer)

    def test_status_request_stop_while_running2(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.start_run()
        writer.request_stop()

        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        self.assertTrue(UtilsDataView.is_stop_already_requested())
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())
        self.assertFalse(UtilsDataView.is_no_stop_requested())
        self.assertFalse(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        # writer.finish_run()
        # writer.hard_reset()
        with self.assertRaises(SimulatorRunningException):
            writer.soft_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        # writer.stopping()
        with self.assertRaises(UnexpectedStateChange):
            writer.shut_down()

    def test_status_request_stop_while_running2(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.start_run()
        writer.request_stop()
        writer.finish_run()
        self.check_start_finish(writer)

    def test_start_finish_start_request_hard(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.start_run()
        writer.request_stop()
        writer.hard_reset()
        self.check_start_hard_request(writer)

    def test_start_finish_start_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.start_run()
        writer.request_stop()
        writer.stopping()
        self.check_start_finish_stopping(writer)

    def check_start_finish_stopping(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        with self.assertRaises(UnexpectedStateChange):
            UtilsDataView.is_stop_already_requested()
        self.assertFalse(UtilsDataView.is_user_mode())
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())
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
        writer.stopping()
        writer.shut_down()

        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView.is_user_mode())
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.is_stop_already_requested()
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())
        with self.assertRaises(NotImplementedError):
             UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertFalse(UtilsDataView.is_setup())

        with self.assertRaises(SimulatorShutdownException):
            writer.start_run()
        with self.assertRaises(UnexpectedStateChange):
            writer.finish_run()
        with self.assertRaises(SimulatorShutdownException):
            writer.hard_reset()
        with self.assertRaises(SimulatorShutdownException):
            writer.soft_reset()
        with self.assertRaises(SimulatorShutdownException):
            writer.request_stop()
        with self.assertRaises(SimulatorShutdownException):
            writer.stopping()
        writer.shut_down()

    def test_start_finish_start_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.start_run()
        writer.stopping()
        self.check_start_finish_stopping(writer)

    def test_start_finish_hard_reset(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.hard_reset()
        self.check_status_hard_reset_after_run(writer)

    def check_status_hard_reset_after_run(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView.is_user_mode())
        with self.assertRaises(UnexpectedStateChange):
            UtilsDataView.is_stop_already_requested()
        UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertTrue(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        # writer.start_run()
        with self.assertRaises(UnexpectedStateChange):
            writer.finish_run()
        with self.assertRaises(UnexpectedStateChange):
            writer.hard_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.soft_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        # writer.stopping() see test_status_stop_after_running_no_reset
        with self.assertRaises(UnexpectedStateChange):
            writer.shut_down()

    def test_start_finish_hard_reset_start(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.hard_reset()
        writer.start_run()
        self.check_test_status_second_run_hard(writer)

    def test_start_finish_hard_reset_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.hard_reset()
        writer.stopping()
        self.check_stopping_after_hard(writer)

    def test_start_finish_soft(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        self.check_soft_reset_after_run(writer)

    def check_soft_reset_after_run(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView.is_user_mode())
        with self.assertRaises(UnexpectedStateChange):
            UtilsDataView.is_stop_already_requested()
        UtilsDataView.check_user_can_act()
        self.assertTrue(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        # writer.start_run()
        with self.assertRaises(UnexpectedStateChange):
            writer.finish_run()
        # writer.hard_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.soft_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        # writer.stopping()
        with self.assertRaises(UnexpectedStateChange):
            writer.shut_down()

    def test_start_finish_soft_start(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        writer.start_run()

        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        self.assertFalse(UtilsDataView.is_stop_already_requested())
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_soft_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        self.assertTrue(UtilsDataView.is_no_stop_requested())
        self.assertTrue(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        # writer.finish_run()
        # writer.hard_reset()
        with self.assertRaises(SimulatorRunningException):
            writer.soft_reset()
        # writer.request_stop()
        # writer.stopping()
        with self.assertRaises(UnexpectedStateChange):
            writer.shut_down()

    def test_start_finish_soft_start_finish(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        writer.start_run()
        writer.finish_run()
        self.check_start_finish(writer)

    def test_start_finish_soft_start_hard(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        writer.start_run()
        writer.hard_reset()
        self.check_test_status_second_run_hard(writer)

    def test_start_finish_soft_start_request(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        writer.start_run()
        writer.request_stop()
        self.check_start_soft_request(writer)

    def check_start_soft_request(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        self.assertTrue(UtilsDataView.is_stop_already_requested())
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertTrue(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        self.assertFalse(UtilsDataView.is_no_stop_requested())
        self.assertFalse(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        # writer.finish_run()
        # writer.hard_reset()
        with self.assertRaises(SimulatorRunningException):
            writer.soft_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        # writer.stopping()
        with self.assertRaises(UnexpectedStateChange):
            writer.shut_down()

    def test_start_finish_soft_start_request_finish(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        writer.start_run()
        writer.request_stop()
        writer.finish_run()
        self.check_start_finish(writer)

    def test_start_finish_soft_start_request_hard(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        writer.start_run()
        writer.request_stop()
        writer.hard_reset()
        self.check_start_hard_request(writer)

    def test_start_finish_soft_start_request_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        writer.start_run()
        writer.request_stop()
        writer.stopping()
        self.check_stop_after_running_soft(writer)

    def check_stop_after_running_soft(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        with self.assertRaises(UnexpectedStateChange):
            UtilsDataView.is_stop_already_requested()
        self.assertFalse(UtilsDataView.is_user_mode())
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertTrue(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
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
        writer.stopping()
        writer.shut_down()

        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView.is_user_mode())
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.is_stop_already_requested()
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.check_user_can_act()
        self.assertTrue(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        with self.assertRaises(NotImplementedError):
             UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertFalse(UtilsDataView.is_setup())

        with self.assertRaises(SimulatorShutdownException):
            writer.start_run()
        with self.assertRaises(UnexpectedStateChange):
            writer.finish_run()
        with self.assertRaises(SimulatorShutdownException):
            writer.hard_reset()
        with self.assertRaises(SimulatorShutdownException):
            writer.soft_reset()
        with self.assertRaises(SimulatorShutdownException):
            writer.request_stop()
        with self.assertRaises(SimulatorShutdownException):
            writer.stopping()
        writer.shut_down()

    def test_start_finish_soft_start_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        writer.start_run()
        writer.stopping()
        self.check_stop_after_running_soft(writer)

    def test_start_finish_soft_hard(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        writer.hard_reset()
        self.check_status_hard_reset_after_run(writer)

    def test_start_finish_soft_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.soft_reset()
        writer.stopping()
        self.check_stop_after_running_soft(writer)

    def test_start_finish_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.finish_run()
        writer.stopping()
        self.check_start_finish_stopping(writer)

    def test_start_request(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.request_stop()

        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        self.assertTrue(UtilsDataView.is_stop_already_requested())
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        self.assertFalse(UtilsDataView.is_no_stop_requested())
        self.assertFalse(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        with self.assertRaises(UnexpectedStateChange):
            writer.start_run()
        # writer.finish_run() # see test_status_finish_run
        with self.assertRaises(SimulatorNotRunException):
            writer.hard_reset()
        with self.assertRaises(SimulatorRunningException):
            writer.soft_reset()
        with self.assertRaises(UnexpectedStateChange):
            writer.request_stop()
        # writer.stopping() # See test_status_stop_while_running
        with self.assertRaises(UnexpectedStateChange):
            writer.shut_down()

    def test_start_request_finish(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.request_stop()
        writer.finish_run()
        self.check_start_finish(writer)

    def test_start_request_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.request_stop()
        writer.stopping()
        self.check_stopping(writer)

    def check_stopping(self, writer):
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        with self.assertRaises(UnexpectedStateChange):
            UtilsDataView.is_stop_already_requested()
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_soft_reset())
        # Only set at end of the current run
        self.assertFalse(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
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
        # TODO support second stop?
        writer.stopping()
        writer.shut_down()

        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView.is_user_mode())
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.is_stop_already_requested()
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        with self.assertRaises(NotImplementedError):
             UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertFalse(UtilsDataView.is_setup())

        with self.assertRaises(SimulatorShutdownException):
            writer.start_run()
        with self.assertRaises(UnexpectedStateChange):
            writer.finish_run()
        with self.assertRaises(SimulatorShutdownException):
            writer.hard_reset()
        with self.assertRaises(SimulatorShutdownException):
            writer.soft_reset()
        with self.assertRaises(SimulatorShutdownException):
            writer.request_stop()
        with self.assertRaises(SimulatorShutdownException):
            writer.stopping()

    def test_status_stop_while_running(self):
        writer = UtilsDataWriter.setup()
        writer.start_run()
        writer.stopping()
        self.check_stopping(writer)


    def test_stopping(self):
        writer = UtilsDataWriter.setup()
        writer.stopping()
        self.check_stopping(writer)


    def todelete(self):
        """
        Test all combination of status

        mock         -sr -fr -hr -sr -rs -s  -sd
        setup        +sr
        start_run
        finish_run
        hard_reset
        soft_reset
        request_stop
        stopping
        shut_down
        :return:
        """
        writer.start_run()
        writer.finish_run()
        writer.hard_reset()
        writer.soft_reset()
        writer.request_stop()
        writer.stopping()
        writer.shut_down()


        # Setup


        # Normal run  Setup followed by run



        # hard reset during run
        writer.hard_reset()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertTrue(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        self.assertFalse(UtilsDataView.is_no_stop_requested())
        self.assertTrue(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        writer.finish_run()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView.is_user_mode())
        UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())
        with self.assertRaises(NotImplementedError):
             UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())


        writer.start_run()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        self.assertTrue(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        self.assertFalse(UtilsDataView.is_no_stop_requested())
        self.assertTrue(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        writer.finish_run()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView.is_user_mode())
        UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())
        with self.assertRaises(NotImplementedError):
             UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())


        writer.start_run()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView.is_user_mode())
        with self.assertRaises(SimulatorRunningException):
            UtilsDataView.check_user_can_act()
        # while running may still be in hard reset mode
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertTrue(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())
        self.assertFalse(UtilsDataView.is_no_stop_requested())
        self.assertTrue(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        writer.finish_run()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView.is_user_mode())
        UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())
        with self.assertRaises(NotImplementedError):
             UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertTrue(UtilsDataView.is_setup())

        writer.shut_down()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView.is_user_mode())
        with self.assertRaises(SimulatorShutdownException):
            UtilsDataView.check_user_can_act()
        self.assertFalse(UtilsDataView.is_soft_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())
        with self.assertRaises(NotImplementedError):
             UtilsDataView.is_no_stop_requested()
        self.assertFalse(UtilsDataView.is_running())
        self.assertFalse(UtilsDataView.is_setup())

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
        self.assertEqual(os.path.curdir, UtilsDataView.get_run_dir_path())

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
