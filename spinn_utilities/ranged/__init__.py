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
from .ranged_list import RangedList, function_iterator

__all__ = [
    "AbstractDict", "AbstractList", "DualList", "SingleList", "AbstractSized",
    "AbstractView", "MultipleValuesException", "RangeDictionary",
    "RangedList", "function_iterator"]
