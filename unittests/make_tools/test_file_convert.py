# Copyright (c) 2018 The University of Manchester
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

from spinn_utilities.make_tools.file_converter import FileConverter

ranged_file = "local_ranges.txt"


class TestConverter(unittest.TestCase):

    def setUp(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.chdir(path)

    def test_convert(self):
        file_name = "weird,file.c"
        src = os.path.join("mock_src", file_name)
        dest = os.path.join("modified_src", file_name)
        dict = dest + "dict"
        FileConverter.convert(src, dest, dict, 2000)
        src_lines = sum(1 for line in open(src))
        modified_lines = sum(1 for line in open(dest))
        self.assertEquals(src_lines, modified_lines)
        with open(dict, 'r') as dictfile:
            data = dictfile.read()
        assert("this is ok" in data)
        assert("this is ok" in data)
        assert("this is fine on two lines" in data)
        assert("before comment after comment" in data)
        assert("One line commted" in data)
        assert("this is for alan); so there!" in data)
        assert("Test %u for alan); so there!" in data)
        assert("\\t back off = %u, time between spikes %u" in data)
        assert("the neuron %d has been determined to not spike" in data)
        assert("Inside a loop" in data)
        assert("then a space" in data)
        assert("then a newline simple" in data)
        assert("then a newline plus" in data)
        assert("first" in data)
        assert("second" in data)
        assert("then a backslash comment on a middle line" in data)
        assert("then a standard comment on a middle line" in data)
        assert("comment before" in data)
