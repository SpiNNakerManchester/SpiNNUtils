# Copyright (c) 2018 The University of Manchester
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

import pytest
from spinn_utilities.config_setup import unittest_setup
from spinn_utilities.config_holder import set_config
from spinn_utilities.socket_address import SocketAddress


def test_correct_usage():
    # Test the constructor
    sa1 = SocketAddress("a", 2, 3)
    sa2 = SocketAddress("a", 2, 3)
    sa3 = SocketAddress("b", 2, 3)
    sa4 = SocketAddress("a", 4, 3)
    sa5 = SocketAddress("a", 2, 5)

    # Test the properties
    assert sa1.listen_port == 3
    assert sa1.notify_host_name == "a"
    assert sa1.notify_port_no == 2

    # Test the equality and other basic ops
    assert sa1 == sa1
    assert sa1 == sa2
    assert sa1 != ("a", 2, 3)
    assert sa1 != sa3
    assert sa1 != sa4
    assert sa1 != sa5
    assert repr(sa1) == "SocketAddress('a', 2, 3)"
    assert str(sa1) == "SocketAddress('a', 2, 3)"

    # Test that we can use them as dictionary keys like a tuple
    d = dict()
    d[sa1] = 123
    d[sa2] = 234
    d[sa3] = 345
    d[sa4] = 456
    d[sa5] = 567
    assert len(d) == 4
    assert d[sa1] == 234


def test_wrong_usage():
    sa = SocketAddress(21, 1, 1)
    # Stringified the 12...
    assert sa.notify_host_name == "12"

    with pytest.raises(TypeError):
        SocketAddress("a", "b", 1)
    with pytest.raises(ValueError):
        SocketAddress("a", 1, "a")


def test_using_configs():
    unittest_setup()
    set_config("Database", "notify_port", 31)
    set_config("Database", "notify_hostname", "b")
    set_config("Database", "listen_port", 21)
    sa1 = SocketAddress()
    assert sa1.listen_port == 31
    assert sa1.notify_host_name == "b"
    assert sa1.notify_port_no == 22

