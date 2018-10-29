from spinn_utilities.bytestring_utils import as_hex, as_string


def test_hex():
    raw = b'helloworld'
    hex = as_hex(raw)
    assert '68,65,6c,6c,6f,77,6f,72,6c,64' == hex


def test_string():
    raw = b'helloworld'
    hex = as_string(raw)
    assert '(10)68,65,6c,6c,6f,77,6f,72,6c,64' == hex


def test_start():
    raw = b'helloworld'
    hex = as_string(raw, start=2)
    assert '(10)6c,6c,6f,77,6f,72,6c,64' == hex


def test_end():
    raw = b'helloworld'
    hex = as_string(raw, end=4)
    assert '(10)68,65,6c,6c' == hex


def test_both():
    raw = b'helloworld'
    hex = as_string(raw, start=3, end=6)
    assert '(10)6c,6f,77' == hex
