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

"""
An implementation of a dictionary and a list that support efficiently working
with ranges of values, used to implement efficient collections for PyNN
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
