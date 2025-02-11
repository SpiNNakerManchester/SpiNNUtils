# Copyright (c) 2018 The University of Manchester
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

import pytest
from spinn_utilities.config_setup import unittest_setup
from spinn_utilities.config_holder import set_config
from spinn_utilities.socket_address import SocketAddress


def test_correct_usage() -> None:
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


def test_wrong_usage() -> None:
    sa = SocketAddress(21, 1, 1)  # type: ignore[arg-type]
    # Stringified the 12...
    assert sa.notify_host_name == "21"

    with pytest.raises(ValueError):
        SocketAddress("a", "b", 1)   # type: ignore[arg-type]
    with pytest.raises(ValueError):
        SocketAddress("a", 1, "a")   # type: ignore[arg-type]


def test_using_configs() -> None:
    unittest_setup()
    set_config("Database", "notify_port", "31")
    set_config("Database", "notify_hostname", "b")
    set_config("Database", "listen_port", "21")
    sa1 = SocketAddress()
    assert sa1.listen_port == 21
    assert sa1.notify_host_name == "b"
    assert sa1.notify_port_no == 31
