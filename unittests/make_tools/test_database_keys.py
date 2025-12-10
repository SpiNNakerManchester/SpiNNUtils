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

    def test_check_all(self) -> None:
        unittest_setup()
        class_file = str(sys.modules[self.__module__].__file__)
        this_path = os.path.dirname(os.path.abspath(class_file))
        test_path = os.path.dirname(this_path)
        utils_path = os.path.dirname(test_path)
        all_path = os.path.dirname(utils_path)

        for root, _dirs, files in os.walk(all_path):
            if "logs.sqlite3" in files:
                UtilsDataView.register_binary_search_path(root)
                logs_path = os.path.join(root, "logs.sqlite3")
                with LogSqlLiteDatabase(logs_path, read_only=False) as db:
                    print(db.get_database_keys(), logs_path)
                    # Add this line to corrupt all databases
                    # run all make cleans again and it should disappear
                    # db.set_database_key("£")
