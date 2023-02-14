# Copyright (c) 2018 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
