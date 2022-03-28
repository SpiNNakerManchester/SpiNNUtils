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

    def test_not_there_exception(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.environ["C_LOGS_DICT"] = str(os.path.join(path, "temp.sqlite3"))
        try:
            FileConverter.convert("mistakes", "modified_src", "not_there.c")
            assert False
        except Exception as ex1:
            assert str(ex1) == "Unable to locate source mistakes/not_there.c"

    def test_split_fail(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.environ["C_LOGS_DICT"] = str(os.path.join(path, "temp.sqlite3"))
        try:
            FileConverter.convert("mistakes", "modified_src", "bad_comma.c")
            assert False
        except Exception as ex1:
            assert str(ex1) == (
                'Unexpected line "); at 19 in mistakes/bad_comma.c')

    def test_format_fail(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.environ["C_LOGS_DICT"] = str(os.path.join(path, "temp.sqlite3"))
        try:
            FileConverter.convert("mistakes", "modified_src", "bad_format.c")
            assert False
        except Exception as ex1:
            assert str(ex1) == "Unexpected formatString in %!"

    def test_unclosed_log(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.environ["C_LOGS_DICT"] = str(os.path.join(path, "temp.sqlite3"))
        try:
            FileConverter.convert("mistakes", "modified_src", "unclosed.c")
            assert False
        except Exception as ex1:
            assert str(ex1) == (
                'Unclosed log_info("test %f", -3.0f in mistakes/unclosed.c')

    def test_semi(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.environ["C_LOGS_DICT"] = str(os.path.join(path, "temp.sqlite3"))
        try:
            FileConverter.convert("mistakes", "modified_src", "semi.c")
            assert False
        except Exception as ex1:
            assert str(ex1) == (
                'Semicolumn missing: '
                'log_info("test %f", -3.0f) in mistakes/semi.c')

    def test_open(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.environ["C_LOGS_DICT"] = str(os.path.join(path, "temp.sqlite3"))
        try:
            FileConverter.convert("mistakes", "modified_src", "open.c")
            assert False
        except Exception as ex1:
            assert str(ex1) == "Unclosed block comment in mistakes/open.c"

    def test_too_few(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.environ["C_LOGS_DICT"] = str(os.path.join(path, "temp.sqlite3"))
        try:
            FileConverter.convert("mistakes", "modified_src", "too_few.c")
            assert False
        except Exception as ex1:
            assert str(ex1) == ('Too few parameters in line "test %f %i", '
                                '-1.0f); at 19 in mistakes/too_few.c')

    def test_too_many(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.environ["C_LOGS_DICT"] = str(os.path.join(path, "temp.sqlite3"))
        try:
            FileConverter.convert("mistakes", "modified_src", "too_many.c")
            assert False
        except Exception as ex1:
            assert str(ex1) == ('Too many parameters in line "test %f", -1.0f,'
                                ' 2); at 19 in mistakes/too_many.c')
