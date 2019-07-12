# Copyright (c) 2017-2019 The University of Manchester
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

try:
    from collections.abc import defaultdict
except ImportError:
    from collections import defaultdict
from spinn_utilities.overrides import overrides
from .abstract_matrix import AbstractMatrix


class DemoMatrix(AbstractMatrix):
    __slots__ = [
        "data"]

    def __init__(self):
        self.data = defaultdict(dict)

    @overrides(AbstractMatrix.get_data)
    def get_data(self, x, y):
        return self.data[x][y]

    @overrides(AbstractMatrix.set_data)
    def set_data(self, x, y, value):
        self.data[x][y] = value
