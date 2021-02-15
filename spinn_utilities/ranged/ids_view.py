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


class _IdsView(AbstractView):
    __slots__ = [
        "_ids"]

    def __init__(self, range_dict, ids):
        """ Use :py:meth:`RangeDictionary.view_factory` to create views
        """
        super().__init__(range_dict)
        self._ids = ids

    def __str__(self):
        return "View with IDs: {}".format(self._ids)

    @overrides(AbstractDict.ids)
    def ids(self):
        return list(self._ids)

    @overrides(AbstractDict.get_value)
    def get_value(self, key):
        return self._range_dict.get_list(key).get_single_value_by_ids(
            self._ids)

    @overrides(AbstractDict.set_value)
    def set_value(self, key, value, use_list_as_value=False):
        ranged_list = self._range_dict.get_list(key)
        for _id in self._ids:
            ranged_list.set_value_by_id(id=_id, value=value)

    def set_value_by_ids(self, key, ids, value):
        for _id in ids:
            self._range_dict[key].set_value_by_id(id=_id, value=value)

    @overrides(AbstractDict.iter_all_values)
    def iter_all_values(self, key, update_save=False):
        return self._range_dict.iter_values_by_ids(
            ids=self._ids, key=key, update_save=update_save)

    @overrides(AbstractDict.iter_ranges)
    def iter_ranges(self, key=None):
        return self._range_dict.iter_ranges_by_ids(key=key, ids=self._ids)
