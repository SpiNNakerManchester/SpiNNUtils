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
from spinn_utilities.executable_finder import ExecutableFinder
import pytest


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
    with pytest.raises(KeyError):
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
    with pytest.raises(KeyError):
        ef.get_executable_path("abc.aplx")


def test_logs(tmpdir):
    if "BINARY_LOGS_DIR" not in os.environ:
        os.environ["BINARY_LOGS_DIR"] = tmpdir.strpath
    else:
        # Do not run this test to not upset the report
        return
    a = tmpdir.mkdir("a")
    b = tmpdir.mkdir("b")
    ef = ExecutableFinder([str(a), str(b)])
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
    ef2 = ExecutableFinder([])
    ef2.check_logs()

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
