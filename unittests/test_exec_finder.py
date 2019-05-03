import pytest
from spinn_utilities.executable_finder import ExecutableFinder


def test_create_and_config(tmpdir):
    a = tmpdir.mkdir("a")
    b = tmpdir.mkdir("b")
    ef = ExecutableFinder([str(a), str(b)])
    assert ef.binary_paths == "{} : {}".format(a, b)
    c = tmpdir.mkdir("c")
    ef.add_path(str(c))
    assert ef.binary_paths == "{} : {} : {}".format(a, b, c)


def test_find_in_no_places():
    ef = ExecutableFinder([])
    with pytest.raises(Exception):
        ef.get_executable_path("abc.aplx")


def test_find_in_one_place(tmpdir):
    ef = ExecutableFinder([str(tmpdir)])
    w = tmpdir.join("abc.aplx")
    w.write("any old content")
    assert ef.get_executable_path("abc.aplx") == str(w)


def test_find_in_two_places(tmpdir):
    a = tmpdir.mkdir("a")
    b = tmpdir.mkdir("b")
    ef = ExecutableFinder([str(a), str(b)])
    w1 = tmpdir.join("a/abc.aplx")
    w1.write("any old content")
    w2 = tmpdir.join("b/abc.aplx")
    w2.write("any old content")
    assert ef.get_executable_path("abc.aplx") == str(w1)
    w1.remove()
    assert ef.get_executable_path("abc.aplx") == str(w2)
    w1.write("any old content")
    assert ef.get_executable_path("abc.aplx") == str(w1)
    w2.remove()
    assert ef.get_executable_path("abc.aplx") == str(w1)
    w1.remove()
    with pytest.raises(Exception):
        ef.get_executable_path("abc.aplx")


def test_find_no_duplicates(tmpdir):
    a = tmpdir.mkdir("a")
    b = tmpdir.mkdir("b")
    ef = ExecutableFinder([str(a), str(b)])
    assert ef.binary_paths == "{} : {}".format(a, b)
    ef.add_path(str(a))
    ef.add_path(str(a))
    ef.add_path(str(b))
    ef.add_path(str(b))
    ef.add_path(str(a))
    ef.add_path(str(a))
    ef.add_path(str(b))
    ef.add_path(str(b))
    assert ef.binary_paths == "{} : {}".format(a, b)
