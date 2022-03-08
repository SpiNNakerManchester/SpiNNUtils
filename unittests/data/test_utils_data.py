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
from spinn_utilities.data.utils_data_writer import UtilsDataWriter
from spinn_utilities.data.data_status import DataStatus
from spinn_utilities.config_setup import unittest_setup
from spinn_utilities.exceptions import (
    DataLocked, DataNotYetAvialable, IllegalWriterException, InvalidDirectory)


class TestUtilsData(unittest.TestCase):

    def setUp(cls):
        unittest_setup()

    def test_status(self):
        # NOT_SETUP only reachable on first call or via hack
        UtilsDataWriter.mock()
        self.assertTrue(UtilsDataView._is_mocked())
        # Most is tests return True if mocked
        UtilsDataView._check_user_write()
        self.assertTrue(UtilsDataView._is_running())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_reset())
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_ran_ever()
        with self.assertRaises(NotImplementedError):
            UtilsDataView.is_ran_last()

        writer = UtilsDataWriter.setup()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView._is_running())
        UtilsDataView._check_user_write()
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_reset())
        self.assertFalse(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())

        # Normal run
        writer.start_run()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView._is_running())
        with self.assertRaises(DataLocked):
            UtilsDataView._check_user_write()
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_reset())
        # Only set at end of the current run
        self.assertFalse(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())

        writer.finish_run()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView._is_running())
        UtilsDataView._check_user_write()
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())

        writer.start_run()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView._is_running())
        with self.assertRaises(DataLocked):
            UtilsDataView._check_user_write()
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())

        writer.finish_run()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView._is_running())
        UtilsDataView._check_user_write()
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertFalse(UtilsDataView.is_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())

        # soft reset
        writer.soft_reset()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView._is_running())
        UtilsDataView._check_user_write()
        self.assertTrue(UtilsDataView.is_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())

        writer.start_run()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView._is_running())
        with self.assertRaises(DataLocked):
            UtilsDataView._check_user_write()
        self.assertTrue(UtilsDataView.is_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())

        writer.finish_run()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView._is_running())
        UtilsDataView._check_user_write()
        self.assertFalse(UtilsDataView.is_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())

        # hard reset
        writer.hard_reset()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView._is_running())
        UtilsDataView._check_user_write()
        self.assertTrue(UtilsDataView.is_reset())
        self.assertTrue(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())

        writer.start_run()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView._is_running())
        with self.assertRaises(DataLocked):
            UtilsDataView._check_user_write()
        # while running may still be in hard reset mode
        self.assertTrue(UtilsDataView.is_reset())
        self.assertTrue(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertFalse(UtilsDataView.is_ran_last())

        writer.finish_run()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView._is_running())
        UtilsDataView._check_user_write()
        self.assertFalse(UtilsDataView.is_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())

        # stop
        writer.stopping()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertTrue(UtilsDataView._is_running())
        with self.assertRaises(DataLocked):
            UtilsDataView._check_user_write()
        self.assertFalse(UtilsDataView.is_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())

        writer.shut_down()
        self.assertFalse(UtilsDataView._is_mocked())
        self.assertFalse(UtilsDataView._is_running())
        with self.assertRaises(DataLocked):
            UtilsDataView._check_user_write()
        self.assertFalse(UtilsDataView.is_reset())
        self.assertFalse(UtilsDataView.is_hard_reset())
        self.assertTrue(UtilsDataView.is_ran_ever())
        self.assertTrue(UtilsDataView.is_ran_last())

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
        writer.hard_reset()
        self.assertEqual(ef, UtilsDataView.get_executable_finder())
        UtilsDataWriter.setup()
        self.assertEqual(ef, UtilsDataView.get_executable_finder())
