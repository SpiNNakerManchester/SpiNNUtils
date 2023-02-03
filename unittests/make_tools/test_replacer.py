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

"""
These test depend on unittests/make_tools/replacer_dict/logs.sqlite3

The replacer.sqlite3 file in this directory is created by
unittests/make_tools/test_file_convert.py method test_convert
as unittests/make_tools/convert.sqlite3

It is manually copied and pasted into this directory
so that the unittests are not order dependant

Note: if weird,file.c changes you may have to manually fix the tests
    especially the log_id and row numbers
"""

import math
import unittest
import os
from spinn_utilities.make_tools.replacer import Replacer
from spinn_utilities.make_tools.file_converter import TOKEN

PATH = os.path.dirname(os.path.abspath(__file__))


class TestReplacer(unittest.TestCase):

    def test_replacer(self):
        os.environ["C_LOGS_DICT"] = str(os.path.join(PATH, "replacer.sqlite3"))
        with Replacer() as replacer:
            new = replacer.replace("5")
        assert ("[INFO] (weird,file.c: 37): this is ok" == new)

    def test_not_there_existing(self):
        # Point C_LOGS_DICT to somewhere that does not exist
        os.environ["C_LOGS_DICT"] = str(
            os.path.join(PATH, "foo", "not_there.sqlite3"))
        try:
            Replacer()
            raise NotImplementedError("Should not work!")
        except Exception as ex:
            assert ("Unable to locate c_logs_dict" in str(ex))

    def test_not_there_new(self):
        # Point C_LOGS_DICT to somewhere that does not exist
        os.environ["C_LOGS_DICT"] = str(
            os.path.join(PATH, "foo", "not_there", "bad.sqlite3"))
        try:
            Replacer(True)
            raise NotImplementedError("Should not work!")
        except Exception as ex:
            assert ("Error accessing c_logs_dict" in str(ex))

    def test_tab(self):
        os.environ["C_LOGS_DICT"] = str(os.path.join(PATH, "replacer.sqlite3"))
        with Replacer() as replacer:
            new = replacer.replace("11" + TOKEN + "10" + TOKEN + "20")
        message = "[INFO] (weird,file.c: 57): \t back off = 10, time between"\
                  " spikes 20"
        assert (message == new)

    def test_float(self):
        os.environ["C_LOGS_DICT"] = str(os.path.join(PATH, "replacer.sqlite3"))
        replacer = Replacer()
        new = replacer.replace("2" + TOKEN + "0xc0400000")
        message = "[INFO] (weird,file.c: 31): test -three -3.0"
        assert (message == new)

    def test_double(self):
        os.environ["C_LOGS_DICT"] = str(os.path.join(PATH, "replacer.sqlite3"))
        replacer = Replacer()
        new = replacer.replace(
            "3" + TOKEN + "40379999" + TOKEN + "9999999a")
        message = "[INFO] (weird,file.c: 33): test double 23.6"
        assert (message == new)

    def test_bad(self):
        os.environ["C_LOGS_DICT"] = str(os.path.join(PATH, "replacer.sqlite3"))
        replacer = Replacer()
        new = replacer.replace("1007" + TOKEN + "10")
        # An exception so just output the input
        message = "1007" + TOKEN + "10"
        assert (message == new)

    def near_equals(self, a, b):
        diff = a - b
        if diff == 0:
            return True
        ratio = diff / a
        return abs(ratio) < 0.0000001

    def test_hex_to_float(self):
        """
        Test the converter against hex values returned from Spinnaker

        """
        os.environ["C_LOGS_DICT"] = str(os.path.join(PATH, "replacer.sqlite3"))
        with Replacer() as replacer:
            assert self.near_equals(
                -345443332234.13432143, replacer._hex_to_float("d2a0dc0e"))
            assert self.near_equals(
                -2000, replacer._hex_to_float("c4fa0000"))
            assert self.near_equals(
                -1, replacer._hex_to_float("bf800000"))
            assert self.near_equals(
                0, replacer._hex_to_float("0"))
            assert self.near_equals(
                0.00014, replacer._hex_to_float("3912ccf7"))
            assert self.near_equals(
                1, replacer._hex_to_float("3f800000"))
            assert self.near_equals(
                200, replacer._hex_to_float("43480000"))
            assert self.near_equals(
                455424364531.3463460, replacer._hex_to_float("52d412d1"))
            assert float("Inf") == replacer._hex_to_float("7f800000")
            assert 0-float("Inf") == replacer._hex_to_float("ff800000")
            assert math.isnan(replacer._hex_to_float("7fc00000"))
            assert self.near_equals(
                -3, replacer._hex_to_float("0xc0400000"))

    def test_hexes_to_double(self):
        """
        Test the converter against hexes values returned from Spinnaker

        """
        os.environ["C_LOGS_DICT"] = str(os.path.join(PATH, "replacer.sqlite3"))
        with Replacer() as replacer:
            assert self.near_equals(
                0, replacer._hexes_to_double("0", "0"))
            assert self.near_equals(
                455424364531.3463460,
                replacer._hexes_to_double("425a825a", "13fcd62b"))
            assert self.near_equals(
                -455424364531.3463460,
                replacer._hexes_to_double("c25a825a", "13fcd62b"))
            assert self.near_equals(
                23.60, replacer._hexes_to_double("40379999", "9999999a"))
            assert self.near_equals(
                -1, replacer._hexes_to_double("bff00000", "0"))
            assert self.near_equals(
                1, replacer._hexes_to_double("3ff00000", "0"))
            assert self.near_equals(
                0.0000000004,
                replacer._hexes_to_double("3dfb7cdf", "d9d7bdbb"))
