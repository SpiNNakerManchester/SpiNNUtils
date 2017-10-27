from spinn_utilities.ranged.multiple_values_exception \
    import MultipleValuesException


from six import add_metaclass

from spinn_utilities.abstract_base import AbstractBase, abstractmethod


@add_metaclass(AbstractBase)
class AbstractList(object):
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

    In the current version the ids are zero base consecutive numbers so there
    is no difference between value based ids and index based ids
    but this could change in the future
    """

    @abstractmethod
    def iter_ranges(self):
        """
        Fast NOT update safe iterator of the ranges

        :return: yields each range one by one
        """
        pass

    @abstractmethod
    def get_default(self):
        pass

    def __init__(self, size, key=None):
        """
        Constructor for a ranged list.

        :param size: Fixed length of the list
        :param key: The dict key this list covers.
        This is used only for better Exception messages
        """
        self._size = int(round(size))
        self._key = key

    def __len__(self):
        """
        Size of the list, irrespective of actual values

        :return: the initial and Fixed size of the list
        """
        return self._size

    def get_ranges(self):
        return list(self.iter_ranges())

    def get_value_all(self):
        """
        If possible returns a single value shared by the whole list.

        For multiple values use for x in list, iter(list) or list.iter,
        or one of the iter_ranges methods

        :return: Value shared by all elements in the list
        :raises MultipleValuesException If even one elements has a different
        value

        """
        ranges = self.get_ranges()
        if len(ranges) > 1:
            raise MultipleValuesException(
                self._key, ranges[0][2], ranges[1][2])
        return ranges[0][2]

    def _check_id(self, id):
        if id < 0:
            if isinstance(id, int):
                raise IndexError(
                    "The index {0!d} is out of range.".format(id))
            raise TypeError("Invalid argument type {}.".format(type(id)))
        if id >= len(self):
            if isinstance(id, int):
                raise IndexError(
                    "The index {0!d} is out of range.".format(id))
            raise TypeError("Invalid argument type {}.".format(type(id)))

    def _check_slice(self, slice_start, slice_stop):
        if (slice_start > slice_stop and slice_start is not None
                and slice_stop is not None):
            if not isinstance(slice_start, int):
                raise TypeError("Invalid argument type {}."
                                "".format(type(slice_start)))
            if not isinstance(slice_stop, int):
                raise TypeError("Invalid argument type {}."
                                "".format(type(slice_start)))
            raise IndexError(
                "The range_start {0!d} is after the range stop {0!d}."
                "".format(slice_start, slice_stop))
        if slice_start < 0 and slice_start is not None:
            if isinstance(slice_start, int):
                raise IndexError(
                    "The range_start {0!d} is out of range."
                    "".format(slice_start))
            raise TypeError("Invalid argument type {}."
                            "".format(type(slice_start)))
        if slice_stop > len(self) and slice_stop is not None:
            if isinstance(slice_stop, int):
                raise IndexError(
                    "The range_stop {0!d} is out of range."
                    "".format(slice_stop))
            raise TypeError("Invalid argument type {}."
                            "".format(type(slice_stop)))

    @abstractmethod
    def get_value_by_id(self, id):
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

        For multiple values use for x in list, iter(list) or list.iter,
        or one of the iter_ranges methods

        :return: Value shared by all elements in the slice
        :raises MultipleValuesException If even one elements has a different
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

        For multiple values use for x in list, iter(list) or list.iter,
        or one of the iter_ranges methods

        :return: Value shared by all elements with these ids
        :raises MultipleValuesException If even one elements has a different
        value.
        Not thrown if elements outside of the ids have a different value,
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
        :return: yeilds the elements pointed to by ids
        """
        ranges = self.iter_ranges()
        current = ranges.next()
        for id in ids:
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
        for id in range(self._size):
            yield self.get_value_by_id(id)

    def __iter__(self):
        """
        Fast NOT update safe iterator of all elements

        Note: Duplicate/Repeated elements are yielded for each id

        :return: yields each element one by one
        """
        for (start, stop, value) in self.iter_ranges():
            for x in range(stop - start):
                yield value

    def iter_by_slice(self, slice_start, slice_stop):
        """
        Fast NOT update safe iterator of all elements in the slice

        Note: Duplicate/Repeated elements are yielded for each id

        :return: yields each element one by one
        """
        for (start, stop, value) in self.iter_ranges():
            if slice_start < stop and slice_stop >= start:
                first = max(start, slice_start)
                end_point = min(stop, slice_stop)
                for _ in range(end_point - first):
                    yield value

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

    def iter_ranges_by_id(self, id):
        """
        iterator of the range for this id

        Note: The start and stop of the range will be reducded to just the id

        This method purpose is one one a control method can select
        which iterator to use

        :return: yields the one range
        """

        self._check_id(id)
        for (start, stop, value) in self.iter_ranges():
            if id < stop:
                yield (id, id + 1, value)
                break

    def iter_ranges_by_slice(self, slice_start, slice_stop):
        """
         Fast NOT update safe iterator of the ranges covered by this slice

         Note: The start and stop of the range will be reduced to just the
         ids inside the slice

         :return: yields each range one by one
         """
        self._check_slice(slice_start, slice_stop)
        for (_start, _stop, value) in self.iter_ranges():
            if slice_start < _stop:
                yield (max(_start, slice_start), min(_stop, slice_stop),
                       value)
                if slice_stop <= _stop:
                    break

    def iter_ranges_by_ids(self, ids):
        """
         Update safe iterator of the ranges covered by these ids

         For consecutive ids where the elements have the same value a single
         range may be yielded

         Note: The start and stop of the range will be reduced to just the
         ids

         :return: yields each range one by one
         """
        range_pointer = 0
        result = None
        ranges = self.get_ranges()
        for id in ids:
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
                # get ranges againb in case changed
                ranges = self.get_ranges()
            result = (id, id + 1, ranges[range_pointer][2])
        yield result
