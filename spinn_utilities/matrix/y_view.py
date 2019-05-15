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

class YView(object):
    """ A view along a particular y-slice of a 2D matrix.
    """
    __slots__ = [
        "_matrix", "_y"]

    def __init__(self, y, matrix):
        self._y = y
        self._matrix = matrix

    def __getitem__(self, key):
        return self._matrix.get_data(x=key, y=self._y)

    def __setitem__(self, key, value):
        self._matrix.set_data(x=key, y=self._y, value=value)
