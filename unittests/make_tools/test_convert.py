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
import unittest

from spinn_utilities.make_tools.converter import Converter
from spinn_utilities.make_tools.log_sqllite_database import LogSqlLiteDatabase


class TestConverter(unittest.TestCase):

    def setUp(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.chdir(path)
        os.environ["C_LOGS_DICT"] = str(os.path.join(path, "temp.sqlite3"))

    def test_convert(self):
        # Clear the database
        LogSqlLiteDatabase(True)
        src = "mock_src"
        dest = "modified_src"
        formats = os.path.join(src, "formats.c")
        # make sure the first formats is there
        shutil.copyfile("formats.c1", formats)
        Converter.convert(src, dest, True)
        with LogSqlLiteDatabase() as sql:
            single = sql.get_max_log_id()
        # Unchanged file a second time should give same ids
        Converter.convert(src, dest, False)
        with LogSqlLiteDatabase() as sql:
            self.assertEquals(single, sql.get_max_log_id())
        # Now use the second formats which as one extra log and moves 1 down
        shutil.copyfile("formats.c2", formats)
        Converter.convert(src, dest, False)
        with LogSqlLiteDatabase() as sql:
            # Need two more ids for the new log and then changed line number
            self.assertEquals(single + 2, sql.get_max_log_id())

    def test_replace(self):
        src = "mock_src"
        dest = "modified_src"
        c = Converter(src, dest, True)
        path = "/home/me/mock_src/FEC/c_common/fec/mock_src/"
        path = path.replace("/", os.path.sep)
        new_path = "/home/me/mock_src/FEC/c_common/fec/modified_src/"
        new_path = new_path.replace("/", os.path.sep)
        self.assertEqual(new_path, c._any_destination(path))

    def test_double_level(self):
        cwd = os.getcwd()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        weird_dir = os.path.join(dir_path, "foo", "bar")
        os.chdir(weird_dir)
        src = "foo/"
        dest = "bar/"
        c = Converter(src, dest, True)
        c.run()
        weird_dir = os.path.join(dir_path, "foo", "bar", "gamma")
        os.chdir(weird_dir)
        c = Converter(src, dest, True)
        c.run()
        os.chdir(cwd)
