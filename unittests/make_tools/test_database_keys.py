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
        database_path = "/foo/bar/logsG.sqlite3"
        key = LogSqlLiteDatabase.key_from_filename(database_path)
        self.assertEqual("G", key)
        database_file = LogSqlLiteDatabase.filename_by_key("/foo/bar", "G")
        self.assertEqual(database_path, database_file)

    def test_check_all(self) -> None:
        """
        This test is maily intended to be run after automatic_make

        It will check all parallel repositories use unque database keys
        """
        unittest_setup()
        class_file = str(sys.modules[self.__module__].__file__)
        this_path = os.path.dirname(os.path.abspath(class_file))
        test_path = os.path.dirname(this_path)
        utils_path = os.path.dirname(test_path)
        all_path = os.path.dirname(utils_path)

        for root, _dirs, files in os.walk(all_path):
            aplx_found = False
            for file in files:
                if file.endswith(".aplx"):
                    aplx_found = True
            if aplx_found:
                UtilsDataView.register_binary_search_path(root)
                print(root)
        # Hack for test do not copy
        # type: ignore[attr-defined]
        database_map = UtilsDataView._UtilsDataView__data._log_database_paths
        for database_key, database_path in database_map.items():
            print(database_key, database_path)
