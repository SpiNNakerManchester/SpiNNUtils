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

from spinn_utilities.overrides import overrides
from .abstract_dict import AbstractDict
from .abstract_view import AbstractView


class _SliceView(AbstractView):
    __slots__ = [
        "_start", "_stop"]

    def __init__(self, range_dict, start, stop):
        """
        Use :py:meth:`RangeDictionary.view_factory` to create views
        """
        super().__init__(range_dict)
        self._start = start
        self._stop = stop

    def __str__(self):
        return f"View with range: {self._start} to {self._stop}"

    @overrides(AbstractDict.ids)
    def ids(self):
        return range(self._start, self._stop)

    @overrides(AbstractDict.get_value)
    def get_value(self, key):
        return self._range_dict.get_list(key).get_single_value_by_slice(
            slice_start=self._start, slice_stop=self._stop)

    def update_save_iter_all_values(self, key):
        ranged_list = self._range_dict.get_list(key)
        for the_id in self.ids():
            yield ranged_list.get_value_by_id(the_id=the_id)

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
    def set_value(self, key, value, use_list_as_value=False):
        self._range_dict.get_list(key).set_value_by_slice(
            slice_start=self._start, slice_stop=self._stop, value=value,
            use_list_as_value=use_list_as_value)

    @overrides(AbstractDict.iter_ranges)
    def iter_ranges(self, key=None):
        return self._range_dict.iter_ranges_by_slice(
            key=key, slice_start=self._start, slice_stop=self._stop)
