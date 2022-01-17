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

from spinn_utilities.overrides import overrides
from .abstract_dict import AbstractDict
from .abstract_view import AbstractView


class _SliceView(AbstractView):
    __slots__ = [
        "_start", "_stop"]

    def __init__(self, range_dict, start, stop):
        """ Use :py:meth:`RangeDictionary.view_factory` to create views
        """
        super().__init__(range_dict)
        self._start = start
        self._stop = stop

    def __str__(self):
        return "View with range: {} to {}".format(self._start, self._stop)

    @overrides(AbstractDict.indexes)
    def indexes(self):
        return range(self._start, self._stop)

    @overrides(AbstractDict.get_value)
    def get_value(self, key):
        return self._range_dict.get_list(key).get_single_value_by_slice(
            slice_start=self._start, slice_stop=self._stop)

    def update_save_iter_all_values(self, key):
        ranged_list = self._range_dict.get_list(key)
        for id in self.indexes():  # @ReservedAssignment
            yield ranged_list.get_value_by_index(index=id)

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
