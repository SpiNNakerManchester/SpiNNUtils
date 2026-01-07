# Copyright (c) 2018 The University of Manchester
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

"""
These test depend on unittests/make_tools/replacer.sqlite3

The replacer.sqlite3 file in this directory is created by
unittests/make_tools/test_file_convert.py method test_convert
as unittests/make_tools/convert_2.sqlite3

It is manually copied and pasted into this directory
so that the unittests are not order dependant

Note: if weird,file.c changes you may have to manually fix the tests
    especially the log_id and row numbers
"""

import math
import os
import pytest
import tempfile
import unittest

from spinn_utilities.config_setup import unittest_setup
from spinn_utilities.data import UtilsDataView
from spinn_utilities.make_tools.converter import convert
from spinn_utilities.make_tools.file_converter import TOKEN
from spinn_utilities.make_tools.replacer import Replacer

PATH = os.path.dirname(os.path.abspath(__file__))
logs_database = "TO BE SET"


class TestReplacer(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        global logs_database
        src = os.path.join(PATH, "mock_src")
        dest = os.path.join(PATH, "modified_src")
        logs_database = convert(src, dest, PATH, "R")

    @pytest.mark.xdist_group(name="mock_src")
    def test_replacer(self) -> None:
        unittest_setup()
        UtilsDataView._register_log_database("R", logs_database)
        with Replacer() as replacer:
            new = replacer.replace("R5")
        assert ("[INFO] (weird,file.c: 36): this is ok" == new)

    def test_external_empty(self) -> None:
        unittest_setup()
        with tempfile.TemporaryDirectory(
                ignore_cleanup_errors=True) as tmpdirname:
            # Should just be ignored
            UtilsDataView.register_binary_search_path(tmpdirname)
        try:
            with Replacer() as replacer:
                new = replacer.replace("5")
                self.assertEqual("5", new)
                new = replacer.replace("C5")
                self.assertEqual("C5", new)
        except ValueError:
            if 'RUNNER_ENVIRONMENT' in os.environ:
                return
        if 'RUNNER_ENVIRONMENT' in os.environ:
            raise ValueError("Should not have worked")

    @pytest.mark.xdist_group(name="mock_src")
    def test_tab(self) -> None:
        unittest_setup()
        UtilsDataView._register_log_database("R", logs_database)
        with Replacer() as replacer:
            new = replacer.replace("R11" + TOKEN + "10" + TOKEN + "20")
        message = "[INFO] (weird,file.c: 56): \t back off = 10, time between"\
                  " spikes 20"
        assert (message == new)

    @pytest.mark.xdist_group(name="mock_src")
    def test_float(self) -> None:
        unittest_setup()
        UtilsDataView._register_log_database("R", logs_database)
        replacer = Replacer()
        new = replacer.replace("R2" + TOKEN + "0xc0400000")
        message = "[INFO] (weird,file.c: 30): test -three -3.0"
        assert (message == new)

    @pytest.mark.xdist_group(name="mock_src")
    def test_double(self) -> None:
        unittest_setup()
        UtilsDataView._register_log_database("R", logs_database)
        replacer = Replacer()
        new = replacer.replace(
            "R3" + TOKEN + "40379999" + TOKEN + "9999999a")
        message = "[INFO] (weird,file.c: 32): test double 23.6"
        assert (message == new)

    @pytest.mark.xdist_group(name="mock_src")
    def test_bad(self) -> None:
        unittest_setup()
        UtilsDataView._register_log_database("R", logs_database)
        replacer = Replacer()
        new = replacer.replace("R1007" + TOKEN + "10")
        # An exception so just output the input
        message = "R1007" + TOKEN + "10"
        assert (message == new)

    def near_equals(self, a: float, b: float) -> bool:
        diff = a - b
        if diff == 0:
            return True
        ratio = diff / a
        return abs(ratio) < 0.0000001

    @pytest.mark.xdist_group(name="mock_src")
    def test_hex_to_float(self) -> None:
        """
        Test the converter against hex values returned from Spinnaker

        """
        unittest_setup()
        UtilsDataView._register_log_database("R", logs_database)
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

    @pytest.mark.xdist_group(name="mock_src")
    def test_hexes_to_double(self) -> None:
        """
        Test the converter against hexes values returned from Spinnaker

        """
        unittest_setup()
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

    def test_blank(self) -> None:
        unittest_setup()
        replacer = Replacer()
        new = replacer.replace("")
        self.assertEqual("", new)
