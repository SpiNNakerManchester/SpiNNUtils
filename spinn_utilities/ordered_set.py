# Copyright (c) 2017-2019 The University of Manchester
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

from collections import OrderedDict
try:
    # pylint: disable=import-error, no-name-in-module
    from collections.abc import MutableSet
except ImportError:
    from collections import MutableSet  # pylint: disable=no-name-in-module


class OrderedSet(MutableSet):
    __slots__ = (
        "_map",
    )

    def __init__(self, iterable=None):
        # pylint: disable=super-init-not-called
        # Always use OrderedDict as plain dict does not support
        # __reversed__ and key indexing
        self._map = OrderedDict()

        # or is overridden in mutable set; calls add on each element
        if iterable is not None:
            self |= iterable

    def add(self, value):
        if value not in self._map:
            self._map[value] = None

    def discard(self, value):
        if value in self._map:
            self._map.pop(value)

    def __iter__(self):
        return self._map.__iter__()

    def __reversed__(self):
        return self._map.__reversed__()

    def peek(self, last=True):
        if not self._map:  # i.e., is self._map empty?
            raise KeyError('set is empty')
        if last:
            return next(reversed(self))
        else:
            return next(self)

    def __len__(self):
        return len(self._map)

    def __contains__(self, key):
        return key in self._map

    def update(self, iterable):
        for item in iterable:
            self.add(item)

    def pop(self, last=True):  # pylint: disable=arguments-differ
        key = self.peek(last)
        self.discard(key)
        return key

    def __repr__(self):
        if not self._map:  # i.e., is self._map empty?
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and self._map == other._map
        return set(self) == set(other)

    def __ne__(self, other):
        """ Comparison method for comparing ordered sets

        :param other: instance of OrderedSet
        :rtype: None
        """
        return not self.__eq__(other)
