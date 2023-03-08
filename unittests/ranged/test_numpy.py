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

from spinn_utilities.ranged.ranged_list import RangedList
import numpy
import pytest


@pytest.mark.parametrize(
    "ranged_list, range_based", [
        (RangedList(10, numpy.arange(10), use_list_as_value=True), True),
        (RangedList(10, [numpy.arange(10) for _ in range(10)]), False)])
def test_list_of_numpy_list(ranged_list, range_based):
    assert ranged_list.range_based() == range_based
    assert numpy.array_equal(
        ranged_list, [numpy.arange(10) for _ in range(10)])
    assert numpy.array_equal(
        ranged_list.get_single_value_all(), numpy.arange(10))

    result_div = ranged_list / 2
    assert result_div == [numpy.arange(10) / 2 for _ in range(10)]

    ranged_list[5] = 5
    assert ranged_list[5] == 5

    ranged_list[7:9] = 10
    assert ranged_list[7:9] == [10, 10]

    values_by_id = list(ranged_list.iter_by_ids([5, 7, 1]))
    assert len(values_by_id) == 3
    assert values_by_id[0] == 5
    assert values_by_id[1] == 10
    assert numpy.array_equal(values_by_id[2], numpy.arange(10))

    values_by_slice = list(ranged_list.iter_by_slice(4, 7))
    assert len(values_by_slice) == 3
    assert numpy.array_equal(values_by_slice[0], numpy.arange(10))
    assert values_by_slice[1] == 5
    assert numpy.array_equal(values_by_slice[2], numpy.arange(10))

    assert 5 in ranged_list
    assert numpy.arange(10) in ranged_list
    assert ranged_list.count(range(10)) == 7
    assert ranged_list.index(10) == 7
    assert ranged_list.index(numpy.arange(10)) == 0

    with pytest.raises(Exception):
        ranged_list[3] = range(5)
    ranged_list.set_value_by_id(3, range(5))
    assert numpy.array_equal(ranged_list[3], numpy.arange(5))

    ranged_list.set_value_by_slice(
        0, 4, numpy.arange(10), use_list_as_value=True)
    assert ranged_list.count(range(10)) == 7

    assert numpy.array_equal(
        ranged_list.get_single_value_by_slice(0, 5), numpy.arange(10))
    assert numpy.array_equal(
        ranged_list.get_single_value_by_ids([0, 9]), numpy.arange(10))
