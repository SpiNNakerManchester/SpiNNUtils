# Copyright (c) 2021 The University of Manchester
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

from spinn_utilities.helpful_functions import is_singleton
from spinn_utilities.overrides import overrides
from .ranged_list import RangedList


class RangedListOfList(RangedList):

    # pylint: disable=unused-argument
    @staticmethod
    @overrides(RangedList.is_list)
    def is_list(value, size):  # @UnusedVariable
        if callable(value):
            return True
        if is_singleton(value):
            raise TypeError(
                "Value must be an iterable or iterable of iterables")
        try:
            # Must be an iterable
            if len(value) == 0:
                return False
            # All or No values must be singletons
            singleton = is_singleton(value[0])
            for i in range(1, len(value)):
                if singleton != is_singleton(value[1]):
                    raise ValueError(
                        "Illegal mixing of singleton and iterable")
            # A list of all singletons is a single value not a list here!
            return not singleton
        except TypeError:
            raise TypeError(
                "Value must be an iterable or iterable of iterables")
