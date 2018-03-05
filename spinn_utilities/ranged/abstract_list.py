# pylint: disable=redefined-builtin
import numbers
from spinn_utilities.ranged.multiple_values_exception \
    import MultipleValuesException
from spinn_utilities.ranged.abstract_sized import AbstractSized
from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from past.builtins import xrange
from six import add_metaclass


@add_metaclass(AbstractBase)
class AbstractList(AbstractSized):
    """ A ranged implementation of list.

    Functions that change the size of the list are NOT Supported.\
    These include::

        __setitem__ where key >= len
        __delitem__
        append
        extend
        insert
        pop
        remove

    Function that manipulate the list based on values are not supported.\
    These include::

        reverse, __reversed__
        sort

    In the current version the IDs are zero base consecutive numbers so there\
    is no difference between value-based IDs and index-based IDs\
    but this could change in the future.
    """
    __slots__ = [
        "_key"]

    def __init__(self, size, key=None):
        """
        Constructor for a ranged list.

        :param size: Fixed length of the list
        :param key: The dict key this list covers.\
            This is used only for better Exception messages
        """
        super(AbstractList, self).__init__(size)
        self._key = key

    @abstractmethod
    def range_based(self):
        """ Shows if the list is suited to deal with ranges or not.

        All list must implement all the range functions, \
        but there are times when using ranges will probably be slower than \
        using individual values.\
        For example the individual values may be stored in a list in which \
        case the ranges are created on demand.

        :return: True if and only if Ranged based calls are recommended.
        """
        pass

    def __len__(self):
        """ Size of the list, irrespective of actual values

        :return: the initial and Fixed size of the list
        """
        return self._size

    def get_value_all(self):
        """ If possible returns a single value shared by the whole list.

        For multiple values use for x in list, iter(list) or list.iter,\
        or one of the iter_ranges methods

        :return: Value shared by all elements in the list
        :raises MultipleValuesException: \
            If even one elements has a different value
        """
        # This is not elegant code but as the ranges could be created on the
        # fly the best way.
        have_item = False
        only_range = None
        for this_range in self.iter_ranges():
            if have_item:
                # If we can get another range, there must be more than one
                # value, so raise the exception
                raise MultipleValuesException(
                    self._key, only_range[2], this_range[2])
            have_item = True
            only_range = this_range
        if not have_item:
            # Pretend we totally failed
            raise StopIteration()
        # There isn't another range, so return the value from the only range
        return only_range[2]

    @abstractmethod
    def get_value_by_id(self, id):  # @ReservedAssignment
        """ Returns the value for one item in the list

        :param id: One of the IDs of an element in the list
        :type id: int
        :return: The value of that element
        """
        pass

    @abstractmethod
    def get_value_by_slice(self, slice_start, slice_stop):
        """ If possible returns a single value shared by the whole slice list.

        For multiple values use for x in list, iter(list) or list.iter,\
        or one of the iter_ranges methods

        :return: Value shared by all elements in the slice
        :raises MultipleValuesException: If even one elements has a different\
            value. \
            Not thrown if elements outside of the slice have a different value
        """
        pass

    def __getslice__(self, start, stop):
        return list(self.iter_by_slice(start, stop))

    @abstractmethod
    def get_value_by_ids(self, ids):
        """ If possible returns a single value shared by all the IDs.

        For multiple values use ``for x in list``, ``iter(list)``,\
        ``list.iter``, or one of the ``iter_ranges`` methods

        :return: Value shared by all elements with these IDs
        :raises MultipleValuesException: If even one elements has a different\
            value. \
            Not thrown if elements outside of the IDs have a different value,\
            even if these elements are between the ones pointed to by IDs
        """
        pass

    def __getitem__(self, key):
        """ Supports the list[x] to return an element or slice of the list

        :param key: The int ID, or slice
        :return: The element[key] or the slice
        """

        # If the key is a slice, get the values from the slice
        if isinstance(key, slice):

            # If the slice is continuous, use the continuous slice getter
            if slice.step is None or slice.step == 1:
                return list(self.iter_by_slice(
                    slice_start=slice.start, slice_stop=slice.stop))

            # Otherwise get the items one by one using the start, stop, and
            # step from the slice
            return [self[i] for i in xrange(*key.indices(self._size))]

        # If the key is an int, get the single value
        elif isinstance(key, int):

            # Handle negative indices
            if key < 0:
                key += len(self)
            return self.get_value_by_id(key)
        else:
            raise TypeError("Invalid argument type.")

    def iter_by_ids(self, ids):
        """ Fast not update safe iterator by collection of IDs

        .. note::
            Duplicate/Repeated elements are yielded for each ID

        :param ids: IDs
        :return: yields the elements pointed to by IDs
        """
        ranges = self.iter_ranges()
        (_, stop, value) = next(ranges)
        for id_value in ids:

            # If range is too far ahead, reset to start
            if id_value < stop:
                ranges = self.iter_ranges()
                (_, stop, value) = next(ranges)

            # Move on until the id is in range
            while id_value >= stop:
                (_, stop, value) = next(ranges)

            yield value

    def iter(self):
        """ Update safe iterator of all elements

        .. note::
            Duplicate/Repeated elements are yielded for each ID

        :return: yields each element one by one
        """
        for id_value in xrange(self._size):
            yield self.get_value_by_id(id_value)

    def __iter__(self):
        """ Fast NOT update safe iterator of all elements

        .. note::
            Duplicate/Repeated elements are yielded for each ID

        :return: yields each element one by one
        """
        if self.range_based():
            for (start, stop, value) in self.iter_ranges():
                for _ in xrange(stop - start):
                    yield value
        else:
            for id_value in xrange(self._size):
                yield self.get_value_by_id(id_value)

    def iter_by_slice(self, slice_start, slice_stop):
        """ Fast NOT update safe iterator of all elements in the slice

        .. note::
            Duplicate/Repeated elements are yielded for each ID

        :return: yields each element one by one
        """
        slice_start, slice_stop = self._check_slice_in_range(
            slice_start, slice_stop)
        if self.range_based():
            for (start, stop, value) in \
                    self.iter_ranges_by_slice(slice_start, slice_stop):
                for _ in xrange(start, stop):
                    yield value
        else:
            for id_value in xrange(slice_start, slice_stop):
                yield self.get_value_by_id(id_value)

    def __contains__(self, item):
        return any(value == item for (_, _, value) in self.iter_ranges())

    def count(self, x):
        """ Counts the number of elements in the list with value ``x``

        :param x:
        :return:
        """
        return sum(
            stop - start
            for (start, stop, value) in self.iter_ranges()
            if value == x)

    def index(self, x):
        """ Finds the first ID of the first element in the list with value\
            ``x``

        :param x:
        :return:
        """
        for (start, _, value) in self.iter_ranges():
            if value == x:
                return start
        raise ValueError("{} is not in list".format(x))

    @abstractmethod
    def iter_ranges(self):
        """ Fast *non-update-safe* iterator of the ranges

        :return: yields each range one by one
        """

    def iter_ranges_by_id(self, id):  # @ReservedAssignment
        """
        iterator of the range for this ID

        .. note::
            The start and stop of the range will be reduced to just the ID

        This method purpose is so one a control method can select\
        which iterator to use

        :return: yields the one range
        """

        self._check_id_in_range(id)
        for (_, stop, value) in self.iter_ranges():
            if id < stop:
                yield (id, id + 1, value)
                break

    @abstractmethod
    def iter_ranges_by_slice(self, slice_start, slice_stop):
        """
         Fast NOT update safe iterator of the ranges covered by this slice

         Note: The start and stop of the range will be reduced to just the\
         IDs inside the slice

         :return: yields each range one by one
         """
        pass

    def iter_ranges_by_ids(self, ids):
        """ Fast NOT update safe iterator of the ranges covered by these IDs

        For consecutive IDs where the elements have the same value a single\
        range may be yielded

        .. note::
            The start and stop of the range will be reduced to just the IDs

        :return: yields each range one by one
        """
        range_pointer = 0
        result = None
        ranges = list(self.iter_ranges())
        for id_value in ids:

            # check if ranges reset so too far ahead
            if id_value < ranges[range_pointer][0]:
                range_pointer = 0
                while id_value > ranges[range_pointer][0]:
                    range_pointer += 1

            # check if pointer needs to move on
            while id_value >= ranges[range_pointer][1]:
                range_pointer += 1
            if result is not None:
                if (result[1] == id_value and
                        result[2] == ranges[range_pointer][2]):
                    result = (result[0], id_value + 1, result[2])
                    continue
                yield result
            result = (id_value, id_value + 1, ranges[range_pointer][2])
        yield result

    @abstractmethod
    def get_default(self):
        """ Gets the default value of the list.

        Just in case we later allow to increase the number of elements

        :return: Default value
        """
        pass

    def __add__(self, other):
        """ Support for new_list = list1 + list2

        Applied the add operator over this and other to create a new list

        The values of the new list are created on the fly so any changes to\
        the original lists are reflected.

        :param other: another list
        :type other: AbstractList
        :return: new list
        :rtype: AbstractList
        """
        if isinstance(other, AbstractList):
            return DualList(
                left=self, right=other, operation=lambda x, y: x + y)
        if isinstance(other, numbers.Number):
            return SingleList(a_list=self, operation=lambda x: x + other)
        raise Exception("__add__ operation only supported for other "
                        "RangedLists and numerical Values")

    def __sub__(self, other):
        """ Support for new_list = list1 - list2

        Applied the add operator over this and other to create a new list

        The values of the new list are created on the fly so any changes to\
        the original lists are reflected.

        :param other: another list
        :type other: AbstractList
        :return: new list
        :rtype: AbstractList
        """
        if isinstance(other, AbstractList):
            return DualList(
                left=self, right=other, operation=lambda x, y: x - y)
        if isinstance(other, numbers.Number):
            return SingleList(a_list=self, operation=lambda x: x - other)
        raise Exception("__sub__ operation only supported for other "
                        "RangedLists and numerical Values")

    def __mul__(self, other):
        """ Support for new_list = list1 * list2

        Applied the multiplication operator over this and other

        The values of the new list are created on the fly so any changes to\
        the original lists are reflected.

        :param other: another list
        :type other: AbstractList
        :return: new list
        :rtype: AbstractList
        """
        if isinstance(other, AbstractList):
            return DualList(
                left=self, right=other, operation=lambda x, y: x * y)
        if isinstance(other, numbers.Number):
            return SingleList(a_list=self, operation=lambda x: x * other)
        raise Exception("__mul__ operation only supported for other "
                        "RangedLists and numerical Values")

    def __div__(self, other):
        """ Support for new_list = list1 / list2

        Applied the division operator over this and other to create a new list

        The values of the new list are created on the fly so any changes to\
        the original lists are reflected.

        :param other: another list
        :type other: AbstractList
        :return: new list
        :rtype: AbstractList
        """
        if isinstance(other, AbstractList):
            return DualList(
                left=self, right=other, operation=lambda x, y: x / y)
        if isinstance(other, numbers.Number):
            if other == 0:
                raise ZeroDivisionError()
            return SingleList(a_list=self, operation=lambda x: x / other)
        raise Exception("__div__ operation only supported for other "
                        "RangedLists and numerical Values")

    # Python 3 support
    __truediv__ = __div__

    def __floordiv__(self, other):
        """ Support for new_list = list1 // list2

        Applied the floor division operator over this and other

        :param other: another list
        :type other: AbstractList
        :return: new list
        :rtype: AbstractList
        """
        if isinstance(other, AbstractList):
            return DualList(
                left=self, right=other, operation=lambda x, y: x // y)
        if isinstance(other, numbers.Number):
            if other == 0:
                raise ZeroDivisionError()
            return SingleList(a_list=self, operation=lambda x: x // other)
        raise Exception("__floordiv__ operation only supported for other "
                        "RangedLists and numerical Values")

    def apply_operation(self, operation):
        """
        Applies a function on the list to create a new one

        The values of the new list are created on the fly so any changes to\
        the original lists are reflected.

        :param operation: \
            A function that can be applied over the individual values to\
            create new ones.
        :return: new list
        :rtype: AbstractList
        """
        return SingleList(a_list=self, operation=operation)


@add_metaclass(AbstractBase)
class SingleList(AbstractList):
    """ A List that performs an operation on the elements of another list
    """
    __slots__ = [
        "_a_list", "_operation"]

    def __init__(self, a_list, operation, key=None):
        """
        :param a_list: The list to perform the operation on
        :param operation:\
            A function which takes a single value and returns the result of\
            the operation on that value
        :param key: The dict key this list covers.\
            This is used only for better Exception messages
        """
        super(SingleList, self).__init__(size=len(a_list), key=key)
        self._a_list = a_list
        self._operation = operation

    def range_based(self):
        return self._a_list.range_based()

    def get_value_by_id(self, id):  # @ReservedAssignment
        return self._operation(self._a_list.get_value_by_id(id))

    def get_value_by_slice(self, slice_start, slice_stop):
        return self._operation(self._a_list.get_value_by_slice(
            slice_start, slice_stop))

    def get_value_by_ids(self, ids):
        return self._operation(self._a_list.get_value_by_ids(ids))

    def iter_ranges(self):
        for (start, stop, value) in self._a_list.iter_ranges():
            yield (start, stop, self._operation(value))

    def get_default(self):
        self._operation(self._a_list.get_default())

    def iter_ranges_by_slice(self, slice_start, slice_stop):
        for (start, stop, value) in \
                self._a_list.iter_ranges_by_slice(slice_start, slice_stop):
            yield (start, stop, self._operation(value))


@add_metaclass(AbstractBase)
class DualList(AbstractList):
    """ A list which combines two other lists with an operation.
    """
    __slots__ = [
        "_left", "_operation", "_right"]

    def __init__(self, left, right, operation, key=None):
        """
        :param left: The first list to combine
        :param right: The second list to combine
        :param operation:\
            The operation to perform as a function that takes two values and\
            returns the result of the operation
        :param key:\
            The dict key this list covers.\
            This is used only for better Exception messages
        """
        if len(left) != len(right):
            raise Exception("Two list must have the same size")
        super(DualList, self).__init__(size=len(left), key=key)
        self._left = left
        self._right = right
        self._operation = operation

    def range_based(self):
        return self._left.range_based() and self._right.range_based()

    def get_value_by_id(self, id):  # @ReservedAssignment
        return self._operation(
            self._left.get_value_by_id(id), self._right.get_value_by_id(id))

    def get_value_by_slice(self, slice_start, slice_stop):
        return self._operation(
            self._left.get_value_by_slice(slice_start, slice_stop),
            self._right.get_value_by_slice(slice_start, slice_stop))

    def get_value_by_ids(self, ids):
        return self._operation(
            self._left.get_value_by_ids(ids),
            self._right.get_value_by_ids(ids))

    def iter_by_slice(self, slice_start, slice_stop):
        """ Fast NOT update safe iterator of all elements in the slice

        .. note::
            Duplicate/Repeated elements are yielded for each ID

        :return: yields each element one by one
        """
        slice_start, slice_stop = self._check_slice_in_range(
            slice_start, slice_stop)
        if self._left.range_based():
            if self._right.range_based():

                # Both lists are range based
                for (start, stop, value) in \
                        self.iter_ranges_by_slice(slice_start, slice_stop):
                    for _ in range(start, stop):
                        yield value
            else:

                # Left list is range based, right is not
                left_iter = self._left.iter_ranges_by_slice(
                    slice_start, slice_stop)
                right_iter = self._right.iter_by_slice(slice_start, slice_stop)
                for (start, stop, left_value) in left_iter:
                    for _ in range(start, stop):
                        yield self._operation(left_value, next(right_iter))
        else:
            if self._right.range_based():

                # Right list is range based left is not
                left_iter = self._left.iter_by_slice(
                    slice_start, slice_stop)
                right_iter = self._right.iter_ranges_by_slice(
                    slice_start, slice_stop)
                for (start, stop, right_value) in right_iter:
                    for _ in range(start, stop):
                        yield self._operation(next(left_iter), right_value)
            else:

                # Neither list is range based
                left_iter = self._left.iter_by_slice(slice_start, slice_stop)
                right_iter = self._right.iter_by_slice(slice_start, slice_stop)
                while True:
                    yield self._operation(next(left_iter), next(right_iter))

    def iter_ranges(self):
        left_iter = self._left.iter_ranges()
        right_iter = self._right.iter_ranges()
        return self._merge_ranges(left_iter, right_iter)

    def iter_ranges_by_slice(self, slice_start, slice_stop):
        left_iter = self._left.iter_ranges_by_slice(slice_start, slice_stop)
        right_iter = self._right.iter_ranges_by_slice(slice_start, slice_stop)
        return self._merge_ranges(left_iter, right_iter)

    def _merge_ranges(self, left_iter, right_iter):
        (left_start, left_stop, left_value) = next(left_iter)
        (right_start, right_stop, right_value) = next(right_iter)
        while True:
            yield (max(left_start, right_start),
                   min(left_stop, right_stop),
                   self._operation(left_value, right_value))
            if left_stop < right_stop:
                (left_start, left_stop, left_value) = next(left_iter)
            elif left_stop > right_stop:
                (right_start, right_stop, right_value) = next(right_iter)
            else:
                (left_start, left_stop, left_value) = next(left_iter)
                (right_start, right_stop, right_value) = next(right_iter)

    def get_default(self):
        self._operation(self._left.get_default(), self._right.get_default())
