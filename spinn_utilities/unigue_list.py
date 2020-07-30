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


class UnigueList(list):
    """
    A list that silently ignore the insert of duplciates
    """

    def __init__(self, seq=()):
        """
        Creates a list like object and fills in the intial values igornoring
        duplicates.

        :param iterable seq: initial values to use
        """
        list.__init__([])
        for p_object in seq:
            self.append(p_object)

    def append(self, p_object):
        """
        append object to end if not already in the list

        :param p_object: something to add to the lsit
        """
        if p_object in self:
            return
        super(UnigueList, self).append(p_object)

    def copy(self):
        """
        Make a copy/ clone of this list
        :return: a new list
        :rtype: UnigueList
        """
        new_list = UnigueList(self)
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
            self.remove(p_object)
        super(UnigueList, self).insert(index, p_object)

    def __add__(self, *args, **kwargs):
        """
        Adds the two lists together creating a new unigue list

        :param args:
        :param kwargs:
        :return: a new list with a single copy in of all items in the first
        location found
        :rtype: UnigueList
        """
        new_list = UnigueList(self)
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
