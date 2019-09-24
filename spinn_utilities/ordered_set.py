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

import sys

if sys.version_info >= (3, 6):
    from collections.abc import MutableSet
    from collections import OrderedDict

else:
    from collections import MutableSet

    # Only need Node if we dont have an ordered dict
    class _Node(object):
        __slots__ = (
            "_key", "_prev_node", "_next_node"
        )

        def __init__(self, key, prev_node, next_node):
            self._key = key
            self._prev_node = prev_node
            self._next_node = next_node

        @property
        def key(self):
            return self._key

        @property
        def prev_node(self):
            return self._prev_node

        @prev_node.setter
        def prev_node(self, prev_node):
            self._prev_node = prev_node

        @property
        def next_node(self):
            return self._next_node

        @next_node.setter
        def next_node(self, next_node):
            self._next_node = next_node


class OrderedSet(MutableSet):
    if sys.version_info >= (3, 6):

        # Depend on an ordered dict
        __slots__ = ("_map")

        def __init__(self, iterable=None):
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

    else:  # if sys.version_info >= (3, 6):

        # As Python 2.7 does not have an order dict we need a linked list
        __slots__ = (
            "_end", "_map"
        )

        def __init__(self, iterable=None):
            # sentinel node for doubly linked list
            # prev_node of end points to end of list (for reverse iteration)
            # next_node of end points to start of list (for forward iteration)
            self._end = _Node(None, None, None)
            self._end.prev_node = self._end
            self._end.next_node = self._end

            # key --> _Node
            self._map = dict()

            # or is overridden in mutable set; calls add on each element
            if iterable is not None:
                self |= iterable

        def add(self, value):
            if value not in self._map:
                end_prev = self._end.prev_node
                new_node = _Node(value, end_prev, self._end)
                self._map[value] = new_node
                end_prev.next_node = new_node
                self._end.prev_node = new_node

        def discard(self, value):
            if value in self._map:
                node = self._map.pop(value)
                prev_node = node.prev_node
                next_node = node.next_node
                node.prev_node.next_node = next_node
                node.next_node.prev_node = prev_node

        def __iter__(self):
            curr = self._end.next_node
            while curr is not self._end:
                yield curr.key
                curr = curr.next_node

        def __reversed__(self):
            curr = self._end.prev_node
            while curr is not self._end:
                yield curr.key
                curr = curr.prev_node

        @property
        def as_list(self):
            """
            Shows the sets as a list.

            Main use is to allow debuggers easier access at the set.

            Note: This list is disconnected so will not reflect any changes
                to the original set.

            :return: Set as a list
            """
            return list(self)

        def peek(self, last=True):
            if not self._map:  # i.e., is self._map empty?
                raise KeyError('set is empty')
            return self._end.prev_node.key if last else self._end.next_node.key

    # Functions which work regradless if self._map is ordered

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
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)

    def __ne__(self, other):
        """ Comparison method for comparing ordered sets

        :param other: instance of OrderedSet
        :rtype: None
        """
        return not self.__eq__(other)
