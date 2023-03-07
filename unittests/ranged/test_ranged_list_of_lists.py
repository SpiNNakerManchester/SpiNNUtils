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

import unittest
from spinn_utilities.ranged.ranged_list_of_lists import RangedListOfList


class TestRangeListOfLists(unittest.TestCase):

    def test_simple(self):
        rl = RangedListOfList(4, [1, 2, 3])
        self.assertListEqual([[1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3]],
                             list(rl))
        rl[1] = [2, 4, 6]
        self.assertListEqual([[1, 2, 3], [2, 4, 6], [1, 2, 3], [1, 2, 3]],
                             list(rl))
        rl[0:2] = [[12, 14, 16], [23]]
        self.assertListEqual([[12, 14, 16], [23], [1, 2, 3], [1, 2, 3]],
                             list(rl))
        rl.set_value_by_ids([1, 3], [4, 5, 6])
        self.assertListEqual([[12, 14, 16], [4, 5, 6], [1, 2, 3], [4, 5, 6]],
                             list(rl))

    def test_start_empty(self):
        rl = RangedListOfList(3, [])
        self.assertListEqual([[], [], []], list(rl))
        rl.set_value([[1, 2], [3], [4, 5]])
        self.assertListEqual([[1, 2], [3], [4, 5]], list(rl))

    def test_list_checker(self):
        rl = RangedListOfList(3, [])
        with self.assertRaises(ValueError):
            rl.set_value([[1, 2], [4, 5]])
        with self.assertRaises(ValueError):
            rl.set_value([[1, 2], 2, [4, 5]])
        with self.assertRaises(TypeError):
            rl.set_value(2)
        with self.assertRaises(TypeError):
            rl.set_value("bacon")
