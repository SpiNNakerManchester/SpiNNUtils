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

import os
import sys
import unittest

import spinn_utilities
from spinn_utilities.configs.config_checker import ConfigChecker
from spinn_utilities.configs.config_documentor import ConfigDocumentor
from spinn_utilities.config_setup import unittest_setup


class TestCfgChecker(unittest.TestCase):

    def setUp(self) -> None:
        unittest_setup()

    def test_config_checks(self) -> None:
        spinn_utilities_dir = [spinn_utilities.__path__[0]]
        ConfigChecker(spinn_utilities_dir).check()

    def test_cfg_documentor(self) -> None:
        class_file = sys.modules[self.__module__].__file__
        assert class_file is not None
        abs_class_file = os.path.abspath(class_file)
        class_dir = os.path.dirname(abs_class_file)
        test_file = os.path.join(class_dir, 'test.md')

        documentor = ConfigDocumentor()
        documentor.md_configs(test_file)
