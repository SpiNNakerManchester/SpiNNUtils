# Copyright (c) 2022-2023 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from spinn_utilities.config_setup import unittest_setup
from spinn_utilities.config_holder import (
    get_config_bool, get_config_float, get_config_int, get_config_str,
    set_config)


def test_configs_None():
    unittest_setup()
    set_config("Mode", "Foo", "None")
    set_config("Mode", "Bar", "none")
    assert get_config_str("Mode", "Foo") is None
    assert get_config_str("Mode", "bar") is None
    assert get_config_int("Mode", "Foo") is None
    assert get_config_float("Mode", "Foo") is None
    assert get_config_bool("Mode", "Foo") is None
