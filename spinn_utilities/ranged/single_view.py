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
from __future__ import annotations
from typing import (
    Dict, Generic, Iterable, Iterator, Optional, Tuple, overload,
    TYPE_CHECKING)
from spinn_utilities.overrides import overrides
from .abstract_dict import AbstractDict, T, _StrSeq, _Keys
from .abstract_view import AbstractView
if TYPE_CHECKING:
    from .range_dictionary import RangeDictionary


class _SingleView(AbstractView[T], Generic[T]):
    __slots__ = ("_id", )

    def __init__(self, range_dict: RangeDictionary[T], the_id: int):
        """
        Use :py:meth:`RangeDictionary.view_factory` to create views
        """
        super().__init__(range_dict)
        self._id = the_id

    def __str__(self) -> str:
        return f"View with ID: {self._id}"

    @overrides(AbstractDict.ids)
    def ids(self) -> Iterable[int]:
        return [self._id]

    @overload
    def get_value(self, key: str) -> T:
        ...

    @overload
    def get_value(self, key: Optional[_StrSeq]) -> Dict[str, T]:
        ...

    @overrides(AbstractDict.get_value)
    def get_value(self, key: _Keys):
        if isinstance(key, str):
            return self._range_dict.get_list(key).get_value_by_id(
                the_id=self._id)
        elif key is None:
            return {
                k: self._range_dict.get_list(k).get_value_by_id(
                    the_id=self._id)
                for k in self._range_dict.keys()}
        else:
            return {
                k: self._range_dict.get_list(k).get_value_by_id(
                    the_id=self._id)
                for k in key}

    @overload
    def iter_all_values(self, key: str, update_save=False) -> Iterator[T]:
        ...

    @overload
    def iter_all_values(
            self, key: Optional[_StrSeq], update_save=False) -> Iterator[
                Dict[str, T]]:
        ...

    @overrides(AbstractDict.iter_all_values)
    def iter_all_values(self, key, update_save=False):
        if isinstance(key, str):
            yield self._range_dict.get_list(key).get_value_by_id(
                the_id=self._id)
        else:
            yield self._range_dict.get_values_by_id(key=key, the_id=self._id)

    @overrides(AbstractDict.set_value)
    def set_value(self, key: str, value: T, use_list_as_value=False):
        return self._range_dict.get_list(key).set_value_by_id(
            value=value, the_id=self._id)

    @overload
    def iter_ranges(self, key: str) -> Iterator[Tuple[int, int, T]]:
        ...

    @overload
    def iter_ranges(self, key: Optional[_StrSeq] = None) -> Iterator[
            Tuple[int, int, Dict[str, T]]]:
        ...

    @overrides(AbstractDict.iter_ranges)
    def iter_ranges(self, key=None):
        return self._range_dict.iter_ranges_by_id(key=key, the_id=self._id)
