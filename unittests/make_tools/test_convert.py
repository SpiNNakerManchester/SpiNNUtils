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
import shutil
import sys
import tempfile
import unittest

from spinn_utilities.make_tools.converter import convert
from spinn_utilities.make_tools.log_sqllite_database import LogSqlLiteDatabase


class TestConverter(unittest.TestCase):

    def test_convert(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.chdir(path)
        os.environ["C_LOGS_DICT"] = str(os.path.join(path, "convert.sqlite3"))
        # Clear the database
        LogSqlLiteDatabase(True)
        src = "mock_src"
        dest = "modified_src"
        formats = os.path.join(src, "formats.c")
        # make sure the first formats is there
        shutil.copyfile("formats.c1", formats)
        convert(src, dest, True)
        with LogSqlLiteDatabase() as sql:
            single = sql.get_max_log_id()
        # Unchanged file a second time should give same ids
        convert(src, dest, False)
        with LogSqlLiteDatabase() as sql:
            self.assertEqual(single, sql.get_max_log_id())
        # Now use the second formats which as one extra log and moves 1 down
        shutil.copyfile("formats.c2", formats)
        convert(src, dest, False)
        with LogSqlLiteDatabase() as sql:
            # Need two more ids for the new log and then changed line number
            self.assertEqual(single + 2, sql.get_max_log_id())

    def test_double_level(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.chdir(path)
        os.environ["C_LOGS_DICT"] = tempfile.mktemp()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        src = os.path.join(dir_path, "foo", "bar")
        dest = os.path.join(dir_path, "alpha", "beta")
        e1 = os.path.join(dest, "delta", "empty1.c")
        shutil.rmtree(os.path.join(dir_path, "alpha"), ignore_errors=True)
        self.assertFalse(os.path.exists(e1))
        convert(src, dest, True)
        self.assertTrue(os.path.exists(e1))
        convert(src, dest, True)
