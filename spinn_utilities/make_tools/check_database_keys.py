# Copyright (c) 2026 The University of Manchester
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
from spinn_utilities.data import UtilsDataView


def check_all_log_database_keys() -> None:
    """
    This check is intended to be run after automatic_make

    It will check all parallel repositories use unique database keys
    """
    this_path = os.path.dirname(os.path.abspath(__file__))
    test_path = os.path.dirname(this_path)
    utils_path = os.path.dirname(test_path)
    all_path = os.path.dirname(utils_path)
    # exclude dirs that may have an aplx but not logs database
    excludes = set(["JavaSpiNNaker", "spinnaker_tools",
                    "SpiNNakerManchester.github.io"])
    print("Logs Sqlite Database keys and Paths")
    for root, _dirs, files in os.walk(all_path):
        for exclude in excludes:
            if exclude in _dirs:
                _dirs.remove(exclude)
        aplx_found = False
        for file in files:
            if file.endswith(".aplx"):
                aplx_found = True
        if aplx_found:
            UtilsDataView.register_binary_search_path(root)
    # Hack for test do not copy
    database_map = (
        UtilsDataView._UtilsDataView__data.  # type: ignore[attr-defined]
        _log_database_paths)
    for database_key, database_path in database_map.items():
        print(database_key, database_path)


if __name__ == "__main__":
    check_all_log_database_keys()
