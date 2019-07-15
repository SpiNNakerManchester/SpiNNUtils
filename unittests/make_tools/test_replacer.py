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

import unittest
import os
from spinn_utilities.make_tools.replacer import Replacer
from spinn_utilities.make_tools.file_converter import TOKEN

PATH = os.path.dirname(os.path.abspath(__file__))


class TestReplacer(unittest.TestCase):

    def test_replacer(self):
        replacer = Replacer(os.path.join(PATH, "test.aplx"))
        new = replacer.replace("1001")
        assert ("[INFO] (weird;file.c: 9): this is ok" == new)

    def test_not_there(self):
        replacer = Replacer("not_there.pointer")
        assert ("1001" == replacer.replace("1001"))

    def test_not_extension(self):
        replacer = Replacer(os.path.join(PATH, "test"))
        new = replacer.replace("1014" + TOKEN + "123")
        assert ("[INFO] (weird;file.c: 47): second 123" == new)

    def test_tab(self):
        replacer = Replacer(os.path.join(PATH, "test"))
        new = replacer.replace("1007" + TOKEN + "10" + TOKEN + "20")
        message = "[INFO] (weird;file.c: 29): \t back off = 10, time between"\
                  " spikes 20"
        assert (message == new)
