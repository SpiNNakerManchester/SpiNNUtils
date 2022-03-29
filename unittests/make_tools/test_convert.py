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
            self.assertEquals(single, sql.get_max_log_id())
        # Now use the second formats which as one extra log and moves 1 down
        shutil.copyfile("formats.c2", formats)
        convert(src, dest, False)
        with LogSqlLiteDatabase() as sql:
            # Need two more ids for the new log and then changed line number
            self.assertEquals(single + 2, sql.get_max_log_id())

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
