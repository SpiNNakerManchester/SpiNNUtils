import pytest
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
    assert sa1.__repr__() == "SocketAddress('a', 2, 3)"
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
    sa = SocketAddress(None, 1, 1)
    # Stringified the None...
    assert sa.notify_host_name == "None"

    with pytest.raises(TypeError):
        SocketAddress("a", None, 1)
    with pytest.raises(TypeError):
        SocketAddress("a", 1, None)
