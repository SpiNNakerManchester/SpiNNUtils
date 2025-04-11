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

from testfixtures import LogCapture
import os

from spinn_utilities.config_setup import unittest_setup
from spinn_utilities.config_holder import (
    _check_section_exists,
    get_config_bool, get_config_bool_or_none, get_config_float,
    get_config_float_or_none, get_config_int, get_config_int_or_none,
    get_report_path,
    get_config_str, get_config_str_or_none,  set_config)
from spinn_utilities.exceptions import ConfigException, SpiNNUtilsException
from spinn_utilities.testing import log_checker


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


def test_get_report_path():
    unittest_setup()
    _check_section_exists("Reports")

    set_config("Reports", "foo", "foo.txt")
    path = get_report_path("foo")
    assert path.endswith("foo.txt")

    with LogCapture() as lc:
        path = get_report_path("foo", n_run=2)
        log_checker.assert_logs_warning_contains(
            lc.records, "does not have a (n_run)")
        assert path.endswith("foo.txt")

    set_config("Reports", "foo_run", "foo(n_run).txt")
    path = get_report_path("foo_run")
    assert path.endswith("foo1.txt")
    path = get_report_path("foo_run", n_run=2)
    assert path.endswith("foo2.txt")

    set_config("Reports", "foo_json", "json_files\\foo.json")
    path = get_report_path("foo_json")
    dirs, file = os.path.split(path)
    assert dirs.endswith("json_files")
    assert file == "foo.json"
