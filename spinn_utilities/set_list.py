# Copyright (c) 2020 The University of Manchester
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
    # pylint: disable=import-error, no-name-in-module
    from collections.abc import MutableSet
else:
    from collections import MutableSet  # pylint: disable=no-name-in-module

class SetList(list, MutableSet):
    """
    A object that acts both as a Set and a List where when the rules different
    set take preference.
    """

    __slots__ = ["as_set"]

    def __init__(self, seq=()):
        """
        Creates a list like object and fills in the intial values igornoring
        duplicates.

        :param iterable seq: initial values to use
        """
        list.__init__([])
        self.as_set = set()
        for p_object in seq:
            self.append(p_object)

    def append(self, p_object):
        """
        append object to end if not already in the list

        :param p_object: something to add to the lsit
        """
        if p_object in self.as_set:
            return
        super(SetList, self).append(p_object)
        self.as_set.add(p_object)

    def copy(self):
        """
        Make a copy/ clone of this list
        :return: a new list
        :rtype: UnigueList
        """
        new_list = SetList(self)
        new_list.extend(self)
        return new_list

    def extend(self, iterable):
        """
        extend list by appending elements from the iterable

        :param iterable: iterable
        """
        for p_object in iterable:
            self.append(p_object)

    def insert(self, index, p_object):
        """
        insert object before index
        
        note:  If the object was already in the list it is removed and then
        reinserted in the requested place. Therefor this call could cause items
        lower than index to move while items higher than index may not move.

        :param int index: (new) location for the object
        :param p_object: object to add in
        """
        if p_object in self:
            super(SetList, self).remove(p_object)
        else:
            self.as_set.add(p_object)
        super(SetList, self).insert(index, p_object)

    def __add__(self, *args, **kwargs):
        """
        Adds the two lists together creating a new unigue list

        :param args:
        :param kwargs:
        :return: a new list with a single copy in of all items in the first
        location found
        :rtype: UnigueList
        """
        new_list = SetList(self)
        new_list.extend(args[0])
        return new_list

    def __iadd__(self, *args, **kwargs):
        """ inplace add which ignores duplicates
        :return: a new list with a single copy in of all items in the first
        location found
        :rtype: UnigueList
        """
        self.extend(args[0])
        return self

    def __setitem__(self, *args, **kwargs):
        """
        insert object before index

        note:  If the object was already in the list it is removed and then
        reinserted in the requested place. Therefor this call could cause items
        lower than index to move while items higher than index may not move.

        :param int index: (new) location for the object
        :param p_object: object to add in
        """
        self.insert(args[0], args[1])

    def __imul__(self, *args, **kwargs):
        """"
        Multiplication typicaly just adds duplicate copies so is ingnored
        :rtype: UnigueList
        """
        return self

    def add(self, *args, **kwargs):
        """
        Add an element to a set.

        This has no effect if the element is already present.
        """
        self.append(args[0])

    def clear(self, *args, **kwargs):
        """ Remove all elements from this set. """
        super(SetList, self).clear()
        self.as_set.clear()

    def difference(self, *args, **kwargs):
        """
        Return the difference of two or more sets as a new set.

        (i.e. all elements that are in this set but not the others.)
        """
        return SetList(self.as_set.difference(*args, **kwargs))

    def difference_update(self, *args, **kwargs):
        """ Remove all elements of another set from this set.
        """
        for p_object in args[0]:
            self.remove(p_object)

    def discard(self, *args, **kwargs):
        """
        Remove an element from a set if it is a member.

        If the element is not a member, do nothing.
        """
        if args[0] in self.as_set:
            self.as_set.remove(*args, **kwargs)
            super(SetList, self).remove(*args, **kwargs)

    def intersection(self, *args, **kwargs):
        """
        Return the intersection of two sets as a new set.

        (i.e. all elements that are in both sets.)
        """
        return SetList(self.as_set.intersection(*args, **kwargs))

    #def intersection_update(self, *args, **kwargs):
    #    """ Update a set with the intersection of itself and another. """
    #    togo = self.as_set.difference(*args, **kwargs)
    #    for p_object in togo:
    #        self.remove(p_object)

    def isdisjoint(self, *args, **kwargs):
        """ Return True if two sets have a null intersection. """
        return self.as_set.isdisjoint(*args, **kwargs)

    def issubset(self, *args, **kwargs):
        """ Report whether another set contains this set. """
        return self.as_set.issubset(*args, **kwargs)

    def issuperset(self, *args, **kwargs):
        """ Report whether this set contains another set. """
        return self.as_set.issuperset(*args, **kwargs)

    def pop(self, *args, **kwargs):
        """
        Remove and return an arbitrary set element.
        Raises KeyError if the set is empty.
        """
        if not self:  # i.e., is empty?
            raise KeyError('set is empty')
        p_object = super(SetList, self).pop(*args, **kwargs)
        self.as_set.remove(p_object)
        return p_object

    def remove(self, *args, **kwargs):
        """
        Remove an element from a set; it must be a member.

        If the element is not a member, raise a KeyError.
        """
        self.as_set.remove(*args, **kwargs)
        super(SetList, self).remove(*args, **kwargs)

    def symmetric_difference(self, *args, **kwargs):
        """
        Return the symmetric difference of two sets as a new set.

        (i.e. all elements that are in exactly one of the sets.)
        """
        return SetList(self.symmetric_difference(*args, **kwargs))

    #def symmetric_difference_update(self, *args,
    #                                **kwargs):  # real signature unknown
    #    """ Update a set with the symmetric difference of itself and another. """
    #    for p_object in args[0]:
    #        if p_object in self.as_set:
    #            self.remove(p_object)
    #        else:
    #            self.append(p_object)

    def union(self, *args, **kwargs):  # real signature unknown
        """
        Return the union of sets as a new set.

        (i.e. all elements that are in either set.)
        """
        return SetList(self.union(*args, **kwargs))

    def update(self, *args, **kwargs):  # real signature unknown
        """ Update a set with the union of itself and others. """
        self.extend(args[0])

    def __and__(self, *args, **kwargs):  # real signature unknown
        """ Return self&value. """
        self.add(*args, **kwargs)

    def __contains__(self, y):  # real signature unknown; restored from __doc__
        """ x.__contains__(y) <==> y in x. """
        return self.as_set.__contains__(y)

    def __eq__(self, *args, **kwargs): # real signature unknown
        if isinstance(args[0], list):
            return super(SetList, self).__eq__(*args, **kwargs)
        return self.as_set.__eq__(*args, **kwargs)

    def __repr__(self, *args, **kwargs): # real signature unknown
        if self:
            repr = super(SetList, self).__repr__()
            return "SetList(" + repr + ")"
        return "SetList()"

    def peek(self, last=True):
        if not self:  # i.e., is empty?
            raise KeyError('set is empty')
        if last:
            return next(reversed(self))
        else:
            return next(self)

