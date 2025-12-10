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
import unittest

from spinn_utilities.make_tools.log_sqllite_database import LogSqlLiteDatabase

PATH = os.path.dirname(os.path.abspath(__file__))


class TestDatabase(unittest.TestCase):

    @pytest.mark.xdist_group(name="mock_src")
    def test_old(self) -> None:
        class_file = str(sys.modules[self.__module__].__file__)
        path = os.path.dirname(os.path.abspath(class_file))
        os.chdir(path)
        database_path = str(os.path.join(path, "old.sqlite3"))
        # Clear the database
        with LogSqlLiteDatabase(database_path) as sql:
            self.assertSetEqual(set([""]), sql.get_database_keys())
