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

"""
An implementation of a dictionary and a list that support efficiently working\
with ranges of values, used to implement efficient collections for PyNN\
population views and assemblies.
"""

from .abstract_dict import AbstractDict
from .abstract_list import AbstractList, DualList, SingleList
from .abstract_sized import AbstractSized
from .abstract_view import AbstractView
from .multiple_values_exception import MultipleValuesException
from .range_dictionary import RangeDictionary
from .ranged_list import RangedList
from .ranged_list_of_lists import RangedListOfList

__all__ = [
    "AbstractDict", "AbstractList", "DualList", "SingleList", "AbstractSized",
    "AbstractView", "MultipleValuesException", "RangeDictionary",
    "RangedList", "RangedListOfList"]
