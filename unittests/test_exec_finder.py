# Copyright (c) 2017 The University of Manchester
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

import os
import pytest
from spinn_utilities.executable_finder import ExecutableFinder


def test_create_and_config(tmpdir):
    a = tmpdir.mkdir("a")
    b = tmpdir.mkdir("b")
    ef = ExecutableFinder()
    ef.add_path(str(a))
    ef.add_path(str(b))
    assert ef.binary_paths == "{} : {}".format(a, b)
    c = tmpdir.mkdir("c")
    ef.add_path(str(c))
    assert ef.binary_paths == "{} : {} : {}".format(a, b, c)


def test_find_in_no_places():
    ef = ExecutableFinder()
    with pytest.raises(KeyError):
        ef.get_executable_path("abc.aplx")


def test_find_in_one_place(tmpdir):
    ef = ExecutableFinder()
    ef.add_path(str(tmpdir))
    wa = tmpdir.join("abc.aplx")
    wa.write("any old content")
    wb = tmpdir.join("bca.aplx")
    wb.write("any old content")
    assert ef.get_executable_path("abc.aplx") == str(wa)
    p = ef.get_executable_paths("abc.aplx,bca.aplx,cab.aplx")
    assert p == [wa, wb]


def test_find_in_two_places(tmpdir):
    a = tmpdir.mkdir("a")
    b = tmpdir.mkdir("b")
    ef = ExecutableFinder()
    ef.add_path(str(a))
    ef.add_path(str(b))
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
    with pytest.raises(KeyError):
        ef.get_executable_path("abc.aplx")


def test_logs(tmpdir):
    if "BINARY_LOGS_DIR" not in os.environ:

        # test with not logging
        efn = ExecutableFinder()
        efn.check_logs()
        efn.check_logs()

        # test the logging if bad does not block
        os.environ["BINARY_LOGS_DIR"] = "A bad dir that does not exist"
        efx = ExecutableFinder()
        x = tmpdir.mkdir("x")
        w = tmpdir.join("x/abc.aplx")
        w.write("any old content")
        efx.add_path(str(x))
        efx.get_executable_path("abc.aplx")

        # Now use one that does
        os.environ["BINARY_LOGS_DIR"] = tmpdir.strpath

    ef = ExecutableFinder()
    a = tmpdir.mkdir("a")
    b = tmpdir.mkdir("b")
    ef.add_path(str(a))
    ef.add_path(str(b))
    ef.add_path("bad_directory_name")
    w = tmpdir.join("a/abc.aplx")
    w.write("any old content")
    w = tmpdir.join("b/def.aplx")
    w.write("any old content")
    w = tmpdir.join("b/ghi.aplx")
    w.write("any old content")
    w = tmpdir.join("b/jkl.aplx")
    w.write("any old content")
    ef.get_executable_path("abc.aplx")
    ef.get_executable_path("jkl.aplx")
    ef2 = ExecutableFinder()
    ef2.check_logs()
    ef2.clear_logs()


def test_find_no_duplicates(tmpdir):
    ef = ExecutableFinder()
    a = tmpdir.mkdir("a")
    b = tmpdir.mkdir("b")
    ef.add_path(str(a))
    ef.add_path(str(b))
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
