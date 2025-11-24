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

import os
import pytest
import sys
import tempfile
import unittest

from spinn_utilities.make_tools.file_converter import FileConverter
from spinn_utilities.make_tools.log_sqllite_database import LogSqlLiteDatabase
ranged_file = "local_ranges.txt"


class TestConverter(unittest.TestCase):

    @pytest.mark.xdist_group(name="mock_src")
    def test_convert_with_char(self) -> None:
        class_file = str(sys.modules[self.__module__].__file__)
        path = os.path.dirname(os.path.abspath(class_file))
        database_path = str(os.path.join(path, "convert_2.sqlite3"))
        if os.path.exists(database_path):
            os.remove(database_path)
        file_name = "weird,file.c"
        src = os.path.join(path, "mock_src")
        dest = os.path.join(path, "modified_src")
        FileConverter.convert(src, dest, file_name, "t", database_path)
        src_f = os.path.join(src, file_name)
        dest_f = os.path.join(dest, file_name)
        src_lines = sum(1 for line in open(src_f))
        modified_lines = sum(1 for line in open(dest_f))
        self.assertEqual(src_lines, modified_lines)
        with LogSqlLiteDatabase(database_path) as sql:
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

    def test_not_there_exception(self) -> None:
        class_file = str(sys.modules[self.__module__].__file__)
        path = os.path.dirname(os.path.abspath(class_file))
        database_path = tempfile.mktemp()
        # clear the database and create a new one
        LogSqlLiteDatabase(database_path, True)
        src = os.path.join(path, "mistakes")
        dest = os.path.join(path, "modified_src")
        try:
            FileConverter.convert(src, dest, "not_there.c", "t", database_path)
            assert False
        except Exception as ex1:
            self.assertIn("Unable to locate source", str(ex1))
            self.assertIn("mistakes", str(ex1))
            self.assertIn("not_there.c", str(ex1))

    def test_split_fail(self) -> None:
        class_file = str(sys.modules[self.__module__].__file__)
        path = os.path.dirname(os.path.abspath(class_file))
        database_path = tempfile.mktemp()
        src = os.path.join(path, "mistakes")
        dest = os.path.join(path, "modified_src")
        try:
            FileConverter.convert(src, dest, "bad_comma.c", "t", database_path)
            assert False
        except Exception as ex1:
            self.assertIn('Unexpected line "); at 18 in', str(ex1))
            self.assertIn("mistakes", str(ex1))
            self.assertIn("bad_comma.c", str(ex1))

    def test_format_fail(self) -> None:
        class_file = str(sys.modules[self.__module__].__file__)
        path = os.path.dirname(os.path.abspath(class_file))
        src = os.path.join(path, "mistakes")
        dest = os.path.join(path, "modified_src")
        database_path = tempfile.mktemp()
        try:
            FileConverter.convert(src, dest, "bad_format.c", "t", database_path)
            assert False
        except Exception as ex1:
            assert str(ex1) == "Unexpected formatString in %!"

    def test_unclosed_log(self) -> None:
        class_file = str(sys.modules[self.__module__].__file__)
        path = os.path.dirname(os.path.abspath(class_file))
        database_path = tempfile.mktemp()
        # clear the database and create a new one
        LogSqlLiteDatabase(database_path, True)
        src = os.path.join(path, "mistakes")
        dest = os.path.join(path, "modified_src")
        try:
            FileConverter.convert(src, dest, "unclosed.c", "t", database_path)
            assert False
        except Exception as ex1:
            self.assertIn('Unclosed log_info("test %f", -3.0f in ', str(ex1))
            self.assertIn("mistakes/unclosed.c", str(ex1).replace('\\', '/'))

    def test_semi(self) -> None:
        class_file = str(sys.modules[self.__module__].__file__)
        path = os.path.dirname(os.path.abspath(class_file))
        database_path = tempfile.mktemp()
        # clear the database and create a new one
        LogSqlLiteDatabase(database_path, True)
        src = os.path.join(path, "mistakes")
        dest = os.path.join(path, "modified_src")
        try:
            FileConverter.convert(src, dest, "semi.c", "t", database_path)
            assert False
        except Exception as ex1:
            self.assertIn('Semicolumn missing: log_info("test %f", -3.0f)',
                          str(ex1))
            self.assertIn("semi.c", str(ex1))
            self.assertIn("mistakes", str(ex1))

    def test_open(self) -> None:
        class_file = str(sys.modules[self.__module__].__file__)
        path = os.path.dirname(os.path.abspath(class_file))
        database_path = tempfile.mktemp()
        # clear the database and create a new one
        LogSqlLiteDatabase(database_path, True)
        src = os.path.join(path, "mistakes")
        dest = os.path.join(path, "modified_src")
        try:
            FileConverter.convert(src, dest, "open.c", "t", database_path)
            assert False
        except Exception as ex1:
            self.assertIn('Unclosed block comment in ', str(ex1))
            self.assertIn("open.c", str(ex1))
            self.assertIn("mistakes", str(ex1))

    def test_too_few(self) -> None:
        class_file = str(sys.modules[self.__module__].__file__)
        path = os.path.dirname(os.path.abspath(class_file))
        database_path = tempfile.mktemp()
        # clear the database and create a new one
        LogSqlLiteDatabase(database_path,True)
        src = os.path.join(path, "mistakes")
        dest = os.path.join(path, "modified_src")
        try:
            FileConverter.convert(src, dest, "too_few.c", "t", database_path)
            assert False
        except Exception as ex1:
            self.assertIn('Too few parameters in line "test %f %i", -1.0f); ',
                          str(ex1))
            self.assertIn("mistakes", str(ex1))
            self.assertIn("too_few.c", str(ex1))

    def test_too_many(self) -> None:
        class_file = str(sys.modules[self.__module__].__file__)
        path = os.path.dirname(os.path.abspath(class_file))
        database_path = tempfile.mktemp()
        # clear the database and create a new one
        LogSqlLiteDatabase(database_path, True)
        src = os.path.join(path, "mistakes")
        dest = os.path.join(path, "modified_src")
        try:
            FileConverter.convert(src, dest, "too_many.c", "t", database_path)
            assert False
        except Exception as ex1:
            self.assertIn('Too many parameters in line "test %f", -1.0f, 2);',
                          str(ex1))
            self.assertIn("mistakes", str(ex1))
            self.assertIn("too_many.c", str(ex1))
