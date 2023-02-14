# Copyright (c) 2018 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import tempfile
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
        src = os.path.join(path, "mock_src")
        dest = os.path.join(path, "modified_src")
        # clear the database and create a new one
        LogSqlLiteDatabase(True)
        FileConverter.convert(src, dest, file_name)
        src_f = os.path.join(src, file_name)
        dest_f = os.path.join(dest, file_name)
        src_lines = sum(1 for line in open(src_f))
        modified_lines = sum(1 for line in open(dest_f))
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
        os.environ["C_LOGS_DICT"] = tempfile.mktemp()
        # clear the database and create a new one
        LogSqlLiteDatabase(True)
        src = os.path.join(path, "mistakes")
        dest = os.path.join(path, "modified_src")
        try:
            FileConverter.convert(src, dest, "not_there.c")
            assert False
        except Exception as ex1:
            self.assertIn("Unable to locate source", str(ex1))
            self.assertIn("mistakes", str(ex1))
            self.assertIn("not_there.c", str(ex1))

    def test_split_fail(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.environ["C_LOGS_DICT"] = tempfile.mktemp()
        # clear the database and create a new one
        LogSqlLiteDatabase(True)
        src = os.path.join(path, "mistakes")
        dest = os.path.join(path, "modified_src")
        try:
            FileConverter.convert(src, dest, "bad_comma.c")
            assert False
        except Exception as ex1:
            self.assertIn('Unexpected line "); at 18 in', str(ex1))
            self.assertIn("mistakes", str(ex1))
            self.assertIn("bad_comma.c", str(ex1))

    def test_format_fail(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.environ["C_LOGS_DICT"] = tempfile.mktemp()
        # clear the database and create a new one
        LogSqlLiteDatabase(True)
        src = os.path.join(path, "mistakes")
        dest = os.path.join(path, "modified_src")
        try:
            FileConverter.convert(src, dest, "bad_format.c")
            assert False
        except Exception as ex1:
            assert str(ex1) == "Unexpected formatString in %!"

    def test_unclosed_log(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.environ["C_LOGS_DICT"] = tempfile.mktemp()
        # clear the database and create a new one
        LogSqlLiteDatabase(True)
        src = os.path.join(path, "mistakes")
        dest = os.path.join(path, "modified_src")
        try:
            FileConverter.convert(src, dest, "unclosed.c")
            assert False
        except Exception as ex1:
            self.assertIn('Unclosed log_info("test %f", -3.0f in ', str(ex1))
            self.assertIn("mistakes/unclosed.c", str(ex1))

    def test_semi(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.environ["C_LOGS_DICT"] = tempfile.mktemp()
        # clear the database and create a new one
        LogSqlLiteDatabase(True)
        src = os.path.join(path, "mistakes")
        dest = os.path.join(path, "modified_src")
        try:
            FileConverter.convert(src, dest, "semi.c")
            assert False
        except Exception as ex1:
            self.assertIn('Semicolumn missing: log_info("test %f", -3.0f)',
                          str(ex1))
            self.assertIn("semi.c", str(ex1))
            self.assertIn("mistakes", str(ex1))

    def test_open(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.environ["C_LOGS_DICT"] = tempfile.mktemp()
        # clear the database and create a new one
        LogSqlLiteDatabase(True)
        src = os.path.join(path, "mistakes")
        dest = os.path.join(path, "modified_src")
        try:
            FileConverter.convert(src, dest, "open.c")
            assert False
        except Exception as ex1:
            self.assertIn('Unclosed block comment in ', str(ex1))
            self.assertIn("open.c", str(ex1))
            self.assertIn("mistakes", str(ex1))

    def test_too_few(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.environ["C_LOGS_DICT"] = tempfile.mktemp()
        # clear the database and create a new one
        LogSqlLiteDatabase(True)
        src = os.path.join(path, "mistakes")
        dest = os.path.join(path, "modified_src")
        try:
            FileConverter.convert(src, dest, "too_few.c")
            assert False
        except Exception as ex1:
            self.assertIn('Too few parameters in line "test %f %i", -1.0f); ',
                          str(ex1))
            self.assertIn("mistakes", str(ex1))
            self.assertIn("too_few.c", str(ex1))

    def test_too_many(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.environ["C_LOGS_DICT"] = tempfile.mktemp()
        # clear the database and create a new one
        LogSqlLiteDatabase(True)
        src = os.path.join(path, "mistakes")
        dest = os.path.join(path, "modified_src")
        try:
            FileConverter.convert(src, dest, "too_many.c")
            assert False
        except Exception as ex1:
            self.assertIn('Too many parameters in line "test %f", -1.0f, 2);',
                          str(ex1))
            self.assertIn("mistakes", str(ex1))
            self.assertIn("too_many.c", str(ex1))
