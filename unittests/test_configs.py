# Copyright (c) 2022 The University of Manchester
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

from spinn_utilities.config_setup import unittest_setup
from spinn_utilities.config_holder import (
    get_config_bool, get_config_bool_or_none, get_config_float,
    get_config_float_or_none, get_config_int, get_config_int_or_none,
    get_config_str, get_config_str_or_none,  set_config)
from spinn_utilities.exceptions import ConfigException, SpiNNUtilsException


def test_configs_None() -> None:
    unittest_setup()
    set_config("Mapping", "Foo", "None")
    set_config("Mapping", "Bar", "none")
    assert get_config_str_or_none("Mapping", "Foo") is None
    try:
        assert get_config_str("Mapping", "Foo") is None
        raise SpiNNUtilsException("Expected ConfigException")
    except ConfigException:
        pass
    assert get_config_str_or_none("Mapping", "bar") is None
    assert get_config_int_or_none("Mapping", "Foo") is None
    try:
        get_config_int("Mapping", "Foo")
        raise SpiNNUtilsException("Expected ConfigException")
    except ConfigException:
        pass
    assert get_config_float_or_none("Mapping", "Foo") is None
    try:
        assert get_config_float("Mapping", "Foo") is None
        raise SpiNNUtilsException("Expected ConfigException")
    except ConfigException:
        pass
    assert get_config_bool_or_none("Mapping", "Foo") is None
    try:
        assert get_config_bool("Mapping", "Foo") is None
        raise SpiNNUtilsException("Expected ConfigException")
    except ConfigException:
        pass
