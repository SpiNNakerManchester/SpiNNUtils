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
from spinn_utilities.config_holder import (
    add_default_cfg, clear_cfg_files)
from spinn_utilities.data.utils_data_writer import UtilsDataWriter

BASE_CONFIG_FILE = "spinn_utilities.cfg"


def unittest_setup():
    """
    Resets the configurations so only the local default configuration is
    included.

    .. note::
        This file should only be called from `SpiNNUtils/unittests`

    :param unittest_mode: Flag to indicate in unit tests
    """
    clear_cfg_files(True)
    add_spinn_utilities_cfg()
    UtilsDataWriter.mock()


def add_spinn_utilities_cfg():
    add_default_cfg(os.path.join(os.path.dirname(__file__), BASE_CONFIG_FILE))
