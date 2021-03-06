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

import os
import unittest
from spinn_utilities.config_holder import (
    check_python_file, find_double_defaults)
from spinn_utilities.config_setup import reset_configs


class TestCfgChecker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        reset_configs()

    def test_cfg_checker(self):
        module = __import__("spinn_utilities")
        path = module.__file__
        directory = os.path.dirname(path)
        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith(".py"):
                    if file_name == "config_holder.py":
                        continue
                    py_path = os.path.join(root, file_name)
                    check_python_file(py_path)

    def test_double_defaults(self):
        find_double_defaults()
