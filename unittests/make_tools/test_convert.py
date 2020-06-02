# Copyright (c) 2018-2019 The University of Manchester
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
import sys
import unittest

from spinn_utilities.make_tools.converter import Converter
import spinn_utilities.make_tools.converter as converter
from spinn_utilities.make_tools.make_utils import find_dict


class TestConverter(unittest.TestCase):

    def setUp(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.chdir(path)
        os.environ["SPINN_DIRS"] = str(path)

    @staticmethod
    def _max_id(dict_file):
        max_id = 0
        with open(dict_file, 'r') as dict_f:
            for line in dict_f:
                parts = line.strip().split(",", 2)
                if len(parts) == 3 and parts[0].isdigit():
                    id = int(parts[0])
                    if id > max_id:
                        max_id = id
        return max_id

    def test_convert(self):
        src = "mock_src"
        dest = "modified_src"
        Converter.convert(src, dest, True)
        single = self._max_id(find_dict())
        Converter.convert(src, dest, True)
        Converter.convert(src, dest, False)
        Converter.convert(src, dest, False)
        Converter.convert(src, dest, False)
        self.assertEquals(single * 4, self._max_id(find_dict()))

    def test_replace(self):
        src = "mock_src"
        dest = "modified_src"
        c = Converter(src, dest, True)
        path = "/home/me/mock_src/FEC/c_common/fec/mock_src/"
        path = path.replace("/", os.path.sep)
        new_path = "/home/me/mock_src/FEC/c_common/fec/modified_src/"
        new_path = new_path.replace("/", os.path.sep)
        self.assertEqual(new_path, c._any_destination(path))

    def test_double_level(self):
        cwd = os.getcwd()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        weird_dir = os.path.join(dir_path, "foo", "bar")
        os.chdir(weird_dir)
        src = "foo/"
        dest = "bar/"
        dict = find_dict()
        if os.path.exists(os.path.abspath(dict)):
            os.remove(os.path.abspath(dict))
        c = Converter(src, dest, True)
        c.run()
        weird_dir = os.path.join(dir_path, "foo", "bar", "gamma")
        os.chdir(weird_dir)
        c = Converter(src, dest, True)
        c.run()
        os.chdir(cwd)
