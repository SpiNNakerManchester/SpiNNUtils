# Copyright (c) 2017 The University of Manchester
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

from spinn_utilities.ranged import RangeDictionary

defaults = {"a": "alpha", "b": "bravo"}
rd = RangeDictionary(10, defaults)


def test_full() -> None:
    assert [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] == list(rd.ids())


def test_single() -> None:
    view = rd[2]
    assert [2] == list(view.ids())


def test_simple_slice() -> None:
    view = rd[2:6]
    assert [2, 3, 4, 5] == list(view.ids())


def test_extended_slice() -> None:
    view = rd[2:8:2]
    assert [2, 4, 6] == list(view.ids())


def test_tuple() -> None:
    view = rd[2, 4, 7]
    assert [2, 4, 7] == list(view.ids())


def test_unsorted_tuple() -> None:
    view = rd[2, 7, 3]
    assert [2, 7, 3] == list(view.ids())


def test_list() -> None:
    ids = [2, 3, 7]
    view = rd[ids]
    assert [2, 3, 7] == list(view.ids())


def test_double_slice() -> None:
    view1 = rd[2:7]
    assert [2, 3, 4, 5, 6] == list(view1.ids())
    view2 = view1[2:4]
    assert [4, 5] == list(view2.ids())


def test_double_list() -> None:
    ids = [2, 7, 1, 3, 5, 8]
    view1 = rd[ids]
    assert [2, 7, 1, 3, 5, 8] == list(view1.ids())
    view2 = view1[2, 3, 5]
    assert [1, 3, 8] == list(view2.ids())
