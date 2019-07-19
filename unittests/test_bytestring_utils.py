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
