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

import math
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

    def near_equals(self, a, b):
        diff = a - b
        if diff == 0:
            return True
        ratio = diff / a
        return abs(ratio) < 0.0000001

    def test_float_to_hex(self):
        """
        Test the convertor against hex values returned from Spinnaker

        """
        replacer = Replacer(os.path.join(PATH, "test"))
        assert self.near_equals(
            -345443332234.13432143, replacer.hex_to_float("d2a0dc0e"))
        assert self.near_equals(
            -2000, replacer.hex_to_float("c4fa0000"))
        assert self.near_equals(
            -1, replacer.hex_to_float("bf800000"))
        assert self.near_equals(
            0, replacer.hex_to_float("0"))
        assert self.near_equals(
            0.00014, replacer.hex_to_float("3912ccf7"))
        assert self.near_equals(
            1, replacer.hex_to_float("3f800000"))
        assert self.near_equals(
            200, replacer.hex_to_float("43480000"))
        assert self.near_equals(
            455424364531.3463460, replacer.hex_to_float("52d412d1"))
        assert float("Inf") == replacer.hex_to_float("7f800000")
        assert 0-float("Inf") == replacer.hex_to_float("ff800000")
        assert math.isnan(replacer.hex_to_float("7fc00000"))
