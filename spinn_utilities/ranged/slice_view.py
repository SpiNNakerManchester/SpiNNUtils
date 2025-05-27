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
    Dict, Generic, Iterator, Optional, Sequence, Tuple, overload,
    TYPE_CHECKING, Union)
from spinn_utilities.overrides import overrides
from .abstract_dict import AbstractDict, T, _StrSeq, _Keys
from .abstract_view import AbstractView
if TYPE_CHECKING:
    from .range_dictionary import RangeDictionary
    from .ranged_list import _ValueType


class _SliceView(AbstractView[T], Generic[T]):
    __slots__ = ("_start", "_stop")

    def __init__(self, range_dict: RangeDictionary, start: int, stop: int):
        """
        Use :py:meth:`RangeDictionary.view_factory` to create views
        """
        super().__init__(range_dict)
        self._start = start
        self._stop = stop

    def __str__(self) -> str:
        return f"View with range: {self._start} to {self._stop}"

    @overrides(AbstractDict.ids)
    def ids(self) -> Sequence[int]:
        return range(self._start, self._stop)

    @overload
    def get_value(self, key: str) -> T:
        ...

    @overload
    def get_value(self, key: Optional[_StrSeq]) -> Dict[str, T]:
        ...

    @overrides(AbstractDict.get_value)
    def get_value(self, key: _Keys) -> Union[T, Dict[str, T]]:
        if isinstance(key, str):
            return self._range_dict.get_list(key).get_single_value_by_slice(
                slice_start=self._start, slice_stop=self._stop)
        elif key is None:
            return {
                k: self._range_dict.get_list(k).get_single_value_by_slice(
                    slice_start=self._start, slice_stop=self._stop)
                for k in self._range_dict.keys()}
        else:
            return {
                k: self._range_dict.get_list(k).get_single_value_by_slice(
                    slice_start=self._start, slice_stop=self._stop)
                for k in key}

    def update_safe_iter_all_values(self, key: str) -> Iterator[T]:
        """
        Iterate over the Values in a way that will work even between updates

        :param key:
        """
        ranged_list = self._range_dict.get_list(key)
        for the_id in self.ids():
            yield ranged_list.get_value_by_id(the_id=the_id)

    @overload
    def iter_all_values(
            self, key: str, update_safe: bool = False) -> Iterator[T]:
        ...

    @overload
    def iter_all_values(
            self, key: Optional[_StrSeq] = None,
            update_safe: bool = False) -> Iterator[Dict[str, T]]:
        ...

    @overrides(AbstractDict.iter_all_values, extend_defaults=True)
    def iter_all_values(self, key: _Keys = None, update_safe: bool = False
                        ) -> Union[Iterator[T], Iterator[Dict[str, T]]]:
        if isinstance(key, str):
            if update_safe:
                return self.update_safe_iter_all_values(key)
            return self._range_dict.get_list(key).iter_by_slice(
                slice_start=self._start, slice_stop=self._stop)
        return self._range_dict.iter_values_by_slice(
            key=key, slice_start=self._start, slice_stop=self._stop,
            update_safe=update_safe)

    @overrides(AbstractDict.set_value)
    def set_value(self, key: str, value: _ValueType,
                  use_list_as_value: bool = False) -> None:
        self._range_dict.get_list(key).set_value_by_slice(
            slice_start=self._start, slice_stop=self._stop, value=value,
            use_list_as_value=use_list_as_value)

    @overload
    def iter_ranges(self, key: str) -> Iterator[Tuple[int, int, T]]:
        ...

    @overload
    def iter_ranges(self, key: Optional[_StrSeq] = None) -> Iterator[
            Tuple[int, int, Dict[str, T]]]:
        ...

    @overrides(AbstractDict.iter_ranges)
    def iter_ranges(self, key: _Keys = None
                    ) -> Union[Iterator[Tuple[int, int, T]],
                               Iterator[Tuple[int, int, Dict[str, T]]]]:
        return self._range_dict.iter_ranges_by_slice(
            key=key, slice_start=self._start, slice_stop=self._stop)
