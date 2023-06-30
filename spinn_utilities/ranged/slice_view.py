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
from typing import Dict, Generic, Iterable, Optional, Tuple, overload
from spinn_utilities.overrides import overrides
from .abstract_dict import AbstractDict, T, _StrSeq
from .abstract_view import AbstractView
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
    def ids(self) -> Iterable[int]:
        return range(self._start, self._stop)

    @overrides(AbstractDict.get_value)
    def get_value(self, key: str) -> T:
        return self._range_dict.get_list(key).get_single_value_by_slice(
            slice_start=self._start, slice_stop=self._stop)

    def update_save_iter_all_values(self, key: str) -> Iterable[T]:
        ranged_list = self._range_dict.get_list(key)
        for the_id in self.ids():
            yield ranged_list.get_value_by_id(the_id=the_id)

    @overload
    def iter_all_values(
            self, key: str, update_save=False) -> Iterable[T]:
        ...

    @overload
    def iter_all_values(
            self, key: Optional[_StrSeq] = None,
            update_save=False) -> Iterable[Dict[str, T]]:
        ...

    @overrides(AbstractDict.iter_all_values, extend_defaults=True)
    def iter_all_values(self, key=None, update_save=False):
        if isinstance(key, str):
            if update_save:
                return self.update_save_iter_all_values(key)
            return self._range_dict.get_list(key).iter_by_slice(
                slice_start=self._start, slice_stop=self._stop)
        return self._range_dict.iter_values_by_slice(
            key=key, slice_start=self._start, slice_stop=self._stop,
            update_save=update_save)

    @overrides(AbstractDict.set_value)
    def set_value(self, key: str, value: _ValueType, use_list_as_value=False):
        self._range_dict.get_list(key).set_value_by_slice(
            slice_start=self._start, slice_stop=self._stop, value=value,
            use_list_as_value=use_list_as_value)

    @overload
    def iter_ranges(self, key: str) -> Iterable[Tuple[int, int, T]]:
        ...

    @overload
    def iter_ranges(self, key: Optional[_StrSeq] = None) -> Iterable[
            Tuple[int, int, Dict[str, T]]]:
        ...

    @overrides(AbstractDict.iter_ranges)
    def iter_ranges(self, key=None):
        return self._range_dict.iter_ranges_by_slice(
            key=key, slice_start=self._start, slice_stop=self._stop)
