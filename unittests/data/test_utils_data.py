# Copyright (c) 2021 The University of Manchester
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
from spinn_utilities.data.data_status import Data_Status
from spinn_utilities.config_setup import unittest_setup
from spinn_utilities.exceptions import (
    DataNotYetAvialable, InvalidDirectory)


class TestUtilsData(unittest.TestCase):

    def setUp(cls):
        unittest_setup()

    def test_status(self):
        # NOT_SETUP only reachable on first call or via hack
        writer = UtilsDataWriter(Data_Status.MOCKED)
        self.assertEqual(Data_Status.MOCKED, UtilsDataWriter.get_status())
        writer = UtilsDataWriter(Data_Status.SETUP)
        self.assertEqual(Data_Status.SETUP, UtilsDataWriter.get_status())
        writer.hard_reset()
        # self.assertEqual(Data_Status.HARD_RESET, view.status)
        writer.start_run()
        self.assertEqual(Data_Status.IN_RUN, UtilsDataWriter.get_status())
        writer.finish_run()
        self.assertEqual(Data_Status.FINISHED, UtilsDataWriter.get_status())
        writer.stopping()
        self.assertEqual(Data_Status.STOPPING, UtilsDataWriter.get_status())
        writer.shut_down()
        self.assertEqual(Data_Status.SHUTDOWN, UtilsDataWriter.get_status())

    def test_directories_setup(self):
        writer = UtilsDataWriter(Data_Status.MOCKED)
        # setup should clear mocked
        writer.setup()
        with self.assertRaises(DataNotYetAvialable):
            UtilsDataView.get_run_dir_path()

    def test_directories_mocked(self):
        UtilsDataWriter(Data_Status.MOCKED)
        self.assertTrue(os.path.exists(UtilsDataView.get_run_dir_path()))

    def test_set_run_dir_path(self):
        writer = UtilsDataWriter(Data_Status.SETUP)
        writer.setup()
        with self.assertRaises(InvalidDirectory):
            writer.set_run_dir_path("bacon")
        writer.set_run_dir_path(os.path.curdir)
        self.assertEqual(os.path.curdir, UtilsDataView.get_run_dir_path())
        self.assertEqual(os.path.curdir, UtilsDataView.get_run_dir_path())
