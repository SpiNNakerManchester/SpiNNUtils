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


class _SingleView(AbstractView):
    __slots__ = [
        "_id"]

    def __init__(self, range_dict, id):  # @ReservedAssignment
        """ Use :py:meth:`RangeDictionary.view_factory` to create views
        """
        super().__init__(range_dict)
        self._id = id

    def __str__(self):
        return "View with ID: {}".format(self._id)

    @overrides(AbstractDict.indexes)
    def indexes(self):
        return [self._id]

    @overrides(AbstractDict.get_value)
    def get_value(self, key):
        return self._range_dict.get_list(key).get_value_by_index(
            index=self._id)

    @overrides(AbstractDict.iter_all_values)
    def iter_all_values(self, key, update_save=False):
        if isinstance(key, str):
            yield self._range_dict.get_list(key).get_value_by_index(
                index=self._id)
        else:
            yield self._range_dict.get_values_by_id(key=key, id=self._id)

    @overrides(AbstractDict.set_value)
    def set_value(self, key, value, use_list_as_value=False):
        return self._range_dict.get_list(key).set_value_by_id(
            value=value, id=self._id)

    @overrides(AbstractDict.iter_ranges)
    def iter_ranges(self, key=None):
        return self._range_dict.iter_ranges_by_id(key=key, id=self._id)
