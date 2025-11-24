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


import unittest
import os
import tempfile
from spinn_utilities.exceptions import SpiNNUtilsException
from spinn_utilities.make_tools.log_sqllite_database import LogSqlLiteDatabase
from spinn_utilities.make_tools.replacer import Replacer

PATH = os.path.dirname(os.path.abspath(__file__))


class TestLogSqlLiteDatabase(unittest.TestCase):

    def test_keys_single_database(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp1:
            with LogSqlLiteDatabase(tmp1.name, "a") as db:
                keys = db.get_database_keys()
                self.assertIn("a", keys)
            with LogSqlLiteDatabase(tmp1.name, "b") as db:
                keys = db.get_database_keys()
                self.assertIn("b", keys)
                self.assertIn("a", keys)
            Replacer.register_database_path(tmp1.name)

        with tempfile.NamedTemporaryFile() as tmp2:
            with LogSqlLiteDatabase(tmp2.name, "c") as db:
                keys = db.get_database_keys()
                self.assertIn("c", keys)
            Replacer.register_database_path(tmp2.name)
            # Same database multi-ple times is fine
            with LogSqlLiteDatabase(tmp2.name, "c") as db:
                keys = db.get_database_keys()
                self.assertIn("c", keys)
            Replacer.register_database_path(tmp2.name)

        with tempfile.NamedTemporaryFile() as tmp3:
            # Database writer does not check other databases for keys
            with LogSqlLiteDatabase(tmp3.name, "c") as db:
                keys = db.get_database_keys()
                self.assertIn("c", keys)
            # The replacer will go boom
            with self.assertRaises(SpiNNUtilsException):
                Replacer.register_database_path(tmp3.name)
