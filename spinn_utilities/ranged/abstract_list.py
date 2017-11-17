from spinn_utilities.ranged.multiple_values_exception \
    import MultipleValuesException
from spinn_utilities.ranged.abstract_sized import AbstractSized
from spinn_utilities.abstract_base import AbstractBase, abstractmethod

from six import add_metaclass


@add_metaclass(AbstractBase)
class AbstractList(AbstractSized):
    """
    A ranged implemantation of list.

    Functions that change the size of the list are NOT Supported.
    These include
        __setitem__ where key >= len
        __delitem__
        append
        extend
        insert
        pop
        remove

    Function that manipulate the list based on values are not supported.
    These include
        reverse, __reversed__
        sort

    In the current version the ids are zero base consecutive numbers so there\
    is no difference between value based ids and index based ids\
    but this could change in the future
    """

    def __init__(self, size, key=None):
        """
        Constructor for a ranged list.

        :param size: Fixed length of the list
        :param key: The dict key this list covers.\
        This is used only for better Exception messages
        """
        AbstractSized.__init__(self, size)
        self._key = key

    @abstractmethod
    def range_based(self):
        """
        Shows if the list is suited to deal with ranges or not.

        All list must implement all the range functions, \
        but there are times when using ranges will probably be slower than \
        using individual values.
        For example the indivudual values may be stored in a list in which \
        case the ranges are created on demand.

        :return: True if and only if Ranged based calls are recommended.
        """
        pass

    def __len__(self):
        """
        Size of the list, irrespective of actual values

        :return: the initial and Fixed size of the list
        """
        return self._size

    def get_value_all(self):
        """
        If possible returns a single value shared by the whole list.

        For multiple values use for x in list, iter(list) or list.iter,\
        or one of the iter_ranges methods

        :return: Value shared by all elements in the list
        :raises MultipleValuesException If even one elements has a different\
            value
        """
        # This is not ellegant code but as the ranges could be created on the
        # fly the best way.
        iter = self.iter_ranges()
        only_range = iter.next()
        try:
            one_too_many = iter.next()
            raise MultipleValuesException(
                self._key, only_range[2], one_too_many[2])
        except StopIteration:
            return only_range[2]

    @abstractmethod
    def get_value_by_id(self, id):  # @ReservedAssignment
        """
        Returns the value for one item in the list

        :param id: One of the ids of an element in the list
        :type id: int
        :return: The value of that element
        """
        pass

    @abstractmethod
    def get_value_by_slice(self, slice_start, slice_stop):
        """
        If possible returns a single value shared by the whole slice list.

        For multiple values use for x in list, iter(list) or list.iter,\
        or one of the iter_ranges methods

        :return: Value shared by all elements in the slice
        :raises MultipleValuesException If even one elements has a different\
            value.
            Not thrown if elements outside of the slice have a different value
        """
        pass

    def __getslice__(self, start, stop):
        return list(self.iter_by_slice(start, stop))

    @abstractmethod
    def get_value_by_ids(self, ids):
        """
        If possible returns a single value shared by all the ids.

        For multiple values use for x in list, iter(list) or list.iter,\
        or one of the iter_ranges methods

        :return: Value shared by all elements with these ids
        :raises MultipleValuesException If even one elements has a different\
            value.
            Not thrown if elements outside of the ids have a different value,\
            even if these elements are between the ones pointed to by ids
        """
        pass

    def __getitem__(self, key):
        """
        Supports the list[x] to return an element or slice of the list

        :param key: The int id, slice
        :return: The element[key] or the slice
        """
        if isinstance(key, slice):
            if slice.step is None or slice.step == 1:
                return list(self.iter_by_slice(
                    slice_start=slice.start, slice_stop=slice.stop))
            # Get the start, stop, and step from the slice
            return [self[ii] for ii in xrange(*key.indices(self._size))]
        elif isinstance(key, int):
            if key < 0:  # Handle negative indices
                key += len(self)
            return self.get_value_by_id(key)
        else:
            raise TypeError("Invalid argument type.")

    def iter_by_ids(self, ids):
        """
        Fast not update safe iterator by collection of ids

        Note: Duplicate/Repeated elements are yielded for each id

        :param ids: Ids
        :return: yields the elements pointed to by ids
        """
        ranges = self.iter_ranges()
        current = ranges.next()
        for id in ids:  # @ReservedAssignment
            # check if ranges reset so too far ahead
            if id < current[0]:
                ranges = self.iter_ranges()
                current = ranges.next()
                while id > current[0]:
                    current = ranges.next()
            # check if pointer needs to move on
            while id >= current[1]:
                current = ranges.next()
            yield current[2]

    def iter(self):
        """
        Update safe iterator of all elements

        Note: Duplicate/Repeated elements are yielded for each id

        :return: yields each element one by one
        """
        for id in xrange(self._size):  # @ReservedAssignment
            yield self.get_value_by_id(id)

    def __iter__(self):
        """
        Fast NOT update safe iterator of all elements

        Note: Duplicate/Repeated elements are yielded for each id

        :return: yields each element one by one
        """
        if self.range_based():
            for (start, stop, value) in self.iter_ranges():
                for _ in xrange(stop - start):
                    yield value
        else:
            for id in xrange(self._size):  # @ReservedAssignment
                yield self.get_value_by_id(id)

    def iter_by_slice(self, slice_start, slice_stop):
        """
        Fast NOT update safe iterator of all elements in the slice

        Note: Duplicate/Repeated elements are yielded for each id

        :return: yields each element one by one
        """
        slice_start, slice_stop = self._check_slice(slice_start, slice_stop)
        if self.range_based():
            for (start, stop, value) in \
                    self.iter_ranges_by_slice(slice_start, slice_stop):
                for _ in xrange(start, stop):
                    yield value
        else:
            for id in xrange(slice_start, slice_stop):  # @ReservedAssignment
                yield self.get_value_by_id(id)

    def __contains__(self, item):
        for (_, _, value) in self.iter_ranges():
            if value == item:
                return True
        return False

    def count(self, x):
        """
        Counts the number of elements in the list with value x

        :param x:
        :return:
        """
        result = 0
        for (start, stop, value) in self.iter_ranges():
            if value == x:
                result = result + stop - start
        return result

    def index(self, x):
        """
        Finds the first id of the first element in the list with value x
        :param x:
        :return:
        """
        for (start, _, value) in self.iter_ranges():
            if value == x:
                return start
        raise ValueError("{} is not in list".format(x))

    @abstractmethod
    def iter_ranges(self):
        """
        Fast NOT update safe iterator of the ranges

        :return: yields each range one by one
        """
        pass

    def iter_ranges_by_id(self, id):  # @ReservedAssignment
        """
        iterator of the range for this id

        Note: The start and stop of the range will be reduced to just the id

        This method purpose is so one a control method can select\
        which iterator to use

        :return: yields the one range
        """

        self._check_id(id)
        for (_, stop, value) in self.iter_ranges():
            if id < stop:
                yield (id, id + 1, value)
                break

    @abstractmethod
    def iter_ranges_by_slice(self, slice_start, slice_stop):
        """
         Fast NOT update safe iterator of the ranges covered by this slice

         Note: The start and stop of the range will be reduced to just the\
         ids inside the slice

         :return: yields each range one by one
         """
        pass

    def iter_ranges_by_ids(self, ids):
        """
        Fast NOT update safe iterator of the ranges covered by these ids

        For consecutive ids where the elements have the same value a single\
        range may be yielded

        Note: The start and stop of the range will be reduced to just the\
        ids

        :return: yields each range one by one
        """
        range_pointer = 0
        result = None
        ranges = list(self.iter_ranges())
        for id in ids:  # @ReservedAssignment
            # check if ranges reset so too far ahead
            if id < ranges[range_pointer][0]:
                range_pointer = 0
                while id > ranges[range_pointer][0]:
                    range_pointer += 1
            # check if pointer needs to move on
            while id >= ranges[range_pointer][1]:
                range_pointer += 1
            if result is not None:
                if (result[1] == id and
                        result[2] == ranges[range_pointer][2]):
                    result = (result[0], id + 1, result[2])
                    continue
                yield result
            result = (id, id + 1, ranges[range_pointer][2])
        yield result

    @abstractmethod
    def get_default(self):
        """
        Gets the default value of the list.

        Just in case we later allow to increase the number of elements

        :return: Default value
        """
        pass

    def __add__(self, other):
        """
        Support for newlist = list1 + list2

        Applied the add operator over this and other to create a new list

        The values of the new list are created on the fly so any changes to
        the original lists are reflected.

        :param other: another list
        :type other: AbstractList
        :return: new list
        :rtype AbstractList
        """
        from spinn_utilities.ranged.dual_list import DualList
        if isinstance(other, AbstractList):
            return DualList(
                left=self, right=other, operation=lambda x, y: x + y)

    def __sub__(self, other):
        """
        Support for newlist = list1 - list2

        Applied the add operator over this and other to create a new list

        The values of the new list are created on the fly so any changes to
        the original lists are reflected.

        :param other: another list
        :type other: AbstractList
        :return: new list
        :rtype AbstractList
        """
        from spinn_utilities.ranged.dual_list import DualList
        if isinstance(other, AbstractList):
            return DualList(
                left=self, right=other, operation=lambda x, y: x - y)

    def __mul__(self, other):
        """
        Support for newlist = list1 * list2

        Applied the multiplication operator over this and other

        The values of the new list are created on the fly so any changes to
        the original lists are reflected.

        :param other: another list
        :type other: AbstractList
        :return: new list
        :rtype AbstractList
        """
        from spinn_utilities.ranged.dual_list import DualList
        if isinstance(other, AbstractList):
            return DualList(
                left=self, right=other, operation=lambda x, y: x * y)

    def __div__(self, other):
        """
        Support for newlist = list1 / list2

        Applied the division operator over this and other to create a new list

        The values of the new list are created on the fly so any changes to
        the original lists are reflected.

        :param other: another list
        :type other: AbstractList
        :return: new list
        :rtype AbstractList
        """
        from spinn_utilities.ranged.dual_list import DualList
        if isinstance(other, AbstractList):
            return DualList(
                left=self, right=other, operation=lambda x, y: x / y)

    def __floordiv__(self, other):
        """
        Support for newlist = list1 // list2

        Applied the floor division operator over this and other

        :param other: another list
        :type other: AbstractList
        :return: new list
        :rtype AbstractList
        """
        from spinn_utilities.ranged.dual_list import DualList
        if isinstance(other, AbstractList):
            return DualList(
                left=self, right=other, operation=lambda x, y: x // y)

    def apply_operation(self, operation):
        """
        Applies a function on the list to create a new one

        The values of the new list are created on the fly so any changes to
        the original lists are reflected.

        :param operation: A function that can be applied over the indvidual
        values to create new ones.
        :return: new list
        :rtype AbstractList
        """
        from spinn_utilities.ranged.single_list import SingleList
        return SingleList(a_list=self, operation=operation)
