# Copyright (c) 2022 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from spinn_utilities.config_setup import unittest_setup
from spinn_utilities.config_holder import (
    get_config_bool, get_config_float, get_config_int, get_config_str,
    set_config)


def test_configs_None():
    unittest_setup()
    set_config("Mode", "Foo", "None")
    set_config("Mode", "Bar", "none")
    assert get_config_str("Mode", "Foo") is None
    # Don't know if this is desirable but currently None is case sensitive.
    assert get_config_str("Mode", "bar") == "none"
    assert get_config_int("Mode", "Foo") is None
    assert get_config_float("Mode", "Foo") is None
    assert get_config_bool("Mode", "Foo") is None
