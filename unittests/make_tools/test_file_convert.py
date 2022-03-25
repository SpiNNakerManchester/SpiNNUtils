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
from spinn_utilities.make_tools.log_sqllite_database import LogSqlLiteDatabase
ranged_file = "local_ranges.txt"


class TestConverter(unittest.TestCase):

    def test_convert(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.environ["C_LOGS_DICT"] = str(os.path.join(path, "convert.sqlite3"))
        file_name = "weird,file.c"
        src = os.path.join("mock_src", file_name)
        dest = os.path.join("modified_src", file_name)
        # clear the database and create a new one
        LogSqlLiteDatabase(True)
        FileConverter.convert("mock_src", "modified_src", file_name)
        src_lines = sum(1 for line in open(src))
        modified_lines = sum(1 for line in open(dest))
        self.assertEqual(src_lines, modified_lines)
        with LogSqlLiteDatabase() as sql:
            with self.assertRaises(Exception):
                sql.check_original("this is bad")
            sql.check_original("%08x [%3d: (w: %5u (=")
            sql.check_original("test -three %f")
            sql.check_original("test double %F")
            sql.check_original("test slash // %f")
            sql.check_original("this is ok")
            sql.check_original("this is fine on two lines")
            sql.check_original("before comment after comment")
            sql.check_original("One line commented")
            sql.check_original("this is for alan); so there!")
            sql.check_original("Test %u for alan); so there!")
            sql.check_original("\\t back off = %u, time between spikes %u")
            sql.check_original(
                "the neuron %d has been determined to not spike")
            sql.check_original("Inside a loop")
            sql.check_original("then a space")
            sql.check_original("then a newline simple")
            sql.check_original("then a newline plus")
            sql.check_original("first")
            sql.check_original("second %u")
            sql.check_original("then a backslash comment on a middle line")
            sql.check_original("then a standard comment on a middle line")
            sql.check_original("comment before")

    def test_exceptions(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.environ["C_LOGS_DICT"] = str(os.path.join(path, "temp.sqlite3"))
        file_name = "weird,file.c"
        src = os.path.join("mock_src", file_name)
        dest = os.path.join("modified_src", file_name)
        with LogSqlLiteDatabase() as log_database:
            converter = FileConverter(src, dest, log_database)
            try:
                converter.split_by_comma_plus(None, 12)
                assert False
            except Exception as ex1:
                assert "Unexpected line" in str(ex1)
            try:
                converter._short_log(12)
                assert False
            except Exception as ex2:
                assert "Unexpected line" in str(ex2)
            try:
                converter._log_full = '"test %f", -3.0f, 12);'
                converter._log = 'log_info('
                converter._short_log(12)
                assert False
            except Exception as ex2:
                assert "Too many" in str(ex2)
            try:
                converter._log_full = '"test %f %i", -3.0f);'
                converter._short_log(12)
                assert False
            except Exception as ex2:
                assert "Too few" in str(ex2)
            try:
                converter._log_full = '"test %1", -3.0f);'
                converter._short_log(12)
                assert False
            except Exception as ex2:
                assert "Unexpected formatString" in str(ex2)
