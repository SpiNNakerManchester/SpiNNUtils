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
    Dict, Generic, Iterable, Iterator, Optional, Sequence, Tuple,
    overload, TYPE_CHECKING, Union)
from spinn_utilities.overrides import overrides
from .abstract_dict import AbstractDict, _StrSeq, _Keys
from .abstract_list import IdsType
from .abstract_view import AbstractView, T
if TYPE_CHECKING:
    from .range_dictionary import RangeDictionary


class _IdsView(AbstractView[T], Generic[T]):
    __slots__ = ("_ids", )

    def __init__(self, range_dict: RangeDictionary[T], ids: IdsType):
        """
        Use :py:meth:`RangeDictionary.view_factory` to create views
        """
        super().__init__(range_dict)
        self._ids = tuple(ids)

    def __str__(self) -> str:
        return f"View with IDs: {self._ids}"

    @overrides(AbstractDict.ids)
    def ids(self) -> Sequence[int]:
        return self._ids

    @overload
    def get_value(self, key: str) -> T:
        ...

    @overload
    def get_value(self, key: Optional[_StrSeq]) -> Dict[str, T]:
        ...

    @overrides(AbstractDict.get_value)
    def get_value(self, key: _Keys) -> Union[T, Dict[str, T]]:
        if isinstance(key, str):
            return self._range_dict.get_list(key).get_single_value_by_ids(
                self._ids)
        elif key is None:
            return {
                k: self._range_dict.get_list(k).get_single_value_by_ids(
                    self._ids)
                for k in self._range_dict.keys()}
        else:
            return {
                k: self._range_dict.get_list(k).get_single_value_by_ids(
                    self._ids)
                for k in key}

    @overrides(AbstractDict.set_value)
    def set_value(
            self, key: str, value: T, use_list_as_value: bool = False):
        ranged_list = self._range_dict.get_list(key)
        for _id in self._ids:
            ranged_list.set_value_by_id(the_id=_id, value=value)

    def set_value_by_ids(self, key: str, ids: Iterable[int], value: T):
        """
        Sets a already existing key to the new value. For the view specified.

        :param str key:
        :param iter(int) ids:
        :param value:
        """
        rl = self._range_dict[key]
        for _id in ids:
            rl.set_value_by_id(the_id=_id, value=value)

    @overload
    def iter_all_values(self, key: str, update_safe=False) -> Iterator[T]:
        ...

    @overload
    def iter_all_values(self, key: Optional[_StrSeq],
                        update_safe: bool = False) -> Iterator[Dict[str, T]]:
        ...

    @overrides(AbstractDict.iter_all_values)
    def iter_all_values(self, key: _Keys, update_safe: bool = False):
        if isinstance(key, str):
            yield from self._range_dict.iter_values_by_ids(
                ids=self._ids, key=key, update_safe=update_safe)
        else:
            for _id in self._ids:
                yield self._range_dict.get_values_by_id(key, _id)

    @overload
    def iter_ranges(self, key: str) -> Iterator[Tuple[int, int, T]]:
        ...

    @overload
    def iter_ranges(self, key: Optional[_StrSeq] = None) -> Iterator[Tuple[
            int, int, Dict[str, T]]]:
        ...

    @overrides(AbstractDict.iter_ranges)
    def iter_ranges(self, key: _Keys = None
                    ) -> Union[Iterator[Tuple[int, int, T]],
                               Iterator[Tuple[int, int, Dict[str, T]]]]:
        return self._range_dict.iter_ranges_by_ids(key=key, ids=self._ids)
