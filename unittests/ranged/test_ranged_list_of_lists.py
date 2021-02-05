# Copyright (c) 2017-2018 The University of Manchester
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
