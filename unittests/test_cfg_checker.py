# Copyright (c) 2017 The University of Manchester
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
import spinn_utilities
from spinn_utilities.config_holder import run_config_checks
from spinn_utilities.config_setup import unittest_setup


class TestCfgChecker(unittest.TestCase):

    def setUp(self) -> None:
        unittest_setup()

    def test_config_checks(self) -> None:
        spinn_utilities_dir = spinn_utilities.__path__[0]
        run_config_checks(directories=[spinn_utilities_dir],
                          exceptions=[])
