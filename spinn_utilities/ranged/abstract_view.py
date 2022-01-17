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


class AbstractView(AbstractDict):
    """ A view over a ranged dictionary.

    .. note::
        The view may currently be read from only with int and int-collection\
        indices, and only be written to with str indices. This may change to\
        become more permissive in future versions.
    """
    __slots__ = [
        "_range_dict"]

    def __init__(self, range_dict):
        """ Use :py:meth:`RangeDictionary.view_factory` to create views
        """
        self._range_dict = range_dict

    def __getitem__(self, key):
        """ Support for the view[x] based the type of the key

        key is a str is currently not supported use get_value instead. \
        In the future this may be supported to return some kind of list\
        (AbstractList) but how to handle a view there to be determined

        For int and int collections a new view will be returned using\
        :py:meth:`RangeDictionary.view_factory`

        .. note::
            int are indexes into the list of IDs not ID values\
            So for a view with IDs [2,3,4,5] view[2] will have an ID of 4

        :param key: str, int or collection of int
        :return: the single value for the str key or a view
        :raises MultipleValuesException: If the keys has multiple values set.\
            But not if other keys not asked for have multiple values
        """
        if isinstance(key, str):
            raise KeyError("view[key] is not supported Use get_value() ")
        indexes = self.indexes()
        if isinstance(key, (slice, int)):
            return self._range_dict.view_factory(indexes[key])
        selected = []
        for i in key:
            selected.append(indexes[i])
        return self._range_dict.view_factory(selected)

    def __setitem__(self, key, value):
        """ See :py:meth:`AbstractDict.set_value`

        .. note::
            Unlike ``__getitem__``, int based indexes are *not* supported so\
            ``view[int] ==`` will raise an exception
        """
        if isinstance(key, str):
            return self.set_value(key=key, value=value)
        if isinstance(key, (slice, int, tuple, list)):
            raise KeyError("Setting of a slice/index(es) not supported")
        raise KeyError("Unexpected key type: {}".format(type(key)))

    @overrides(AbstractDict.get_default)
    def get_default(self, key):
        return self._range_dict.get_default(key)

    @overrides(AbstractDict.keys)
    def keys(self):
        return self._range_dict.keys()
