# Copyright (c) 2025 The University of Manchester
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
import sys
import unittest

from spinn_utilities.config_setup import unittest_setup
from spinn_utilities.data import UtilsDataView
from spinn_utilities.make_tools.log_sqllite_database import LogSqlLiteDatabase


class TestDatabaseKeys(unittest.TestCase):

    def test_key_from_filename(self) -> None:
        directory = os.path.join("foo", "bar")
        database_path = os.path.join(directory, "logsG.sqlite3")
        key = LogSqlLiteDatabase.key_from_filename(database_path)
        self.assertEqual("G", key)
        database_file = LogSqlLiteDatabase.filename_by_key(directory, "G")
        self.assertEqual(database_path, database_file)

    def test_bad(self) -> None:
        with self.assertRaises(ValueError):
            LogSqlLiteDatabase.key_from_filename("short")
        with self.assertRaises(ValueError):
            LogSqlLiteDatabase.key_from_filename("logs.sqlite3")
