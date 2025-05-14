# Copyright (c) 2021 The University of Manchester
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

from collections.abc import Sized
from typing import (
    Callable, Generic, List, Optional, Sequence, TypeVar, Union)
from typing_extensions import TypeAlias
from spinn_utilities.helpful_functions import is_singleton
from spinn_utilities.overrides import overrides
from .ranged_list import RangedList
#: :meta private:
T = TypeVar("T")
# ranged_list._ValueType but specialised for how we use it here
_ValueType: TypeAlias = Optional[Union[
    List[T], Callable[[int], List[T]], Sequence[List[T]]]]


class RangedListOfList(RangedList[List[T]], Generic[T]):
    """
    A Ranged object for lists of list.
    """
    @overrides(RangedList.listness_check)
    def listness_check(self, value: _ValueType) -> bool:
        if callable(value):
            return True
        if is_singleton(value):
            raise TypeError(
                "Value must be an iterable or iterable of iterables")
        try:
            if not isinstance(value, Sized):
                raise TypeError
            # Must be an iterable
            if len(value) == 0:
                return False
            # All or No values must be singletons
            singleton = is_singleton(value[0])
            for i in range(1, len(value)):
                if singleton != is_singleton(value[i]):
                    raise ValueError(
                        "Illegal mixing of singleton and iterable")
            # A list of all singletons is a single value not a list here!
            return not singleton
        except TypeError as original:
            raise TypeError(
                "Value must be an iterable or iterable of iterables") \
                from original
