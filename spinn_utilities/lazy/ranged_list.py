from spinn_utilities.lazy.list_iterator import ListIterator
from spinn_utilities.lazy.multiple_values_exception \
    import MultipleValuesException


class RangedList(object):
    """
    A lazy implemantation of list.

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
    """

    def __init__(self, size, default):
        self._size = size
        self._default = default
        self._ranges = []
        self._ranges.append((0, size, default))

    def __len__(self):
        return self._size

    def get_data(self, key):
        if key < 0:
            if isinstance(key, int):
                raise IndexError(
                    "The index {0!d} is out of range.".format(key))
            raise TypeError("Invalid argument type {}.".format(type(key)))
        if key >= len(self):
            if isinstance(key, int):
                raise IndexError(
                    "The index {0!d} is out of range.".format(key))
            raise TypeError("Invalid argument type {}.".format(type(key)))
        for (start, stop, value) in self._ranges:
            if key < stop:
                return value

    def get_data_by_range(self, range_start, range_stop):
        if range_start > range_stop:
            temp = range_start
            range_start = range_stop
            range_stop = range_start
        if range_start < 0:
            if isinstance(range_start, int):
                raise IndexError(
                    "The range_start {0!d} is out of range."
                    "".format(range_start))
            raise TypeError("Invalid argument type {}."
                            "".format(type(range_start)))
        if range_stop >= len(self):
            if isinstance(range_stop, int):
                raise IndexError(
                    "The range_stop {0!d} is out of range."
                    "".format(range_stop))
            raise TypeError("Invalid argument type {}."
                            "".format(type(range_stop)))
        result = None
        for (_start, _stop, _value) in self._ranges:
            if range_start < _stop:
                if result is None:
                    result = _value
                elif result != _value:
                    raise MultipleValuesException()
                if range_stop <= _stop:
                    return _value

    def __getslice__(self, start, stop):
        return self.get_data_by_range(start, stop)

    def __getitem__(self, key):
        if isinstance(key, slice):
            # Get the start, stop, and step from the slice
            return [self[ii] for ii in xrange(*key.indices(self._size))]
        elif isinstance(key, int):
            if key < 0:  # Handle negative indices
                key += len(self)
            return self.get_data(key)
        else:
            raise TypeError("Invalid argument type.")

    def set_data(self, key, value):
        """
        Sets the value for a single id to the new value.

        Note: This method only works for a single possitive int id.
        use set or __set__ for slices, tuples, lists and negative indexes
        :param key: Single id
        :type key:int
        :param value:  The value to save
        :type value: anything
        """
        if key < 0:
            raise IndexError(
                "The index {0!d} is out of range.".format(key))
        if key >= len(self):
            raise IndexError(
                "The index {0!d} is out of range.".format(key))
        for index, (start, stop, old_value) in enumerate(self._ranges):
            if key < stop:
                if value == old_value:
                    return  # alreay set as needed so do nothing
                self._ranges[index] = (key, key + 1, value)
                if key +1 < stop:  # Need a new range after the key
                    self._ranges.insert(index + 1, (key + 1, stop, old_value))
                if key > start:   # Need a new range before the key
                    self._ranges.insert(index, (start, key, old_value))
                if index < len(self._ranges) - 1:
                    if self._ranges[index][2] == self._ranges[index+1][2]:
                        self._ranges[index] = (
                            self._ranges[index][0],
                            self._ranges[index + 1][1],
                            self._ranges[index + 1][2])
                        self._ranges.pop(index + 1)
                if index > 0:
                    if self._ranges[index][2] == self._ranges[index-1][2]:
                        self._ranges[index - 1] = (
                            self._ranges[index - 1][0],
                            self._ranges[index][1],
                            self._ranges[index][2])
                        self._ranges.pop(index)
                return

    def set_data_by_range(self, slice_start, slice_stop, value):
        """
        Sets the value for a single range to the new value.

        Note: This method only works for a single possitive int id.
        use set or __set__ for slices, tuples, lists and negative indexes
        :param slice_start: Start of the range
        :type slice_start:int
        :param slice_stop: Exclusive end of the range
        :type slice_stop:int
        :param value:  The value to save
        :type value: anything
        """
        if slice_start > slice_stop:
            temp = slice_start
            slice_start = slice_stop
            slice_stop = slice_start
        if slice_start < 0:
            if isinstance(slice_start, int):
                raise IndexError(
                    "The slice_start {0!d} is out of range."
                    "".format(slice_start))
            raise TypeError("Invalid argument type {}."
                            "".format(type(slice_start)))
        if slice_stop >= len(self):
            if isinstance(slice_stop, int):
                raise IndexError(
                    "The slice_stop {0!d} is out of range."
                    "".format(slice_stop))
            raise TypeError("Invalid argument type {}."
                            "".format(type(slice_stop)))
        index = 0
        # Skip ranges before set range
        while index < len(self._ranges) -1 and \
                (self._ranges[0][1] <= slice_start):
            index += 1

        # Strip of start of first range if needed
        (_start, _stop, old_value) = self._ranges[index]
        if slice_start > _start:  # Need a new range before the key
            if value != old_value:
                self._ranges.insert(index, (_start, slice_start, old_value))
                index += 1
                # Change start of old range but leave value for now
                self._ranges[index] = (slice_start, _stop, old_value)
                (_start, _stop, old_value) = self._ranges[index]
            else:
                # existing already has this value to adjust slice_start
                slice_start = _start

        # Merge with next if overlaps with that one
        while slice_stop > _stop:
            (_start, _stop, old_value) = self._ranges.pop(index+1)
            self._ranges[index] = (slice_start, _stop, old_value)

        # Split of end of merged range if required
        if slice_stop < _stop:
            self._ranges[index] = (slice_start, slice_stop, old_value)
            self._ranges.insert(index+1, (slice_stop, _stop, old_value))

        # merge with previous if same value
        if index > 0 and self._ranges[index-1][2] == value:
            self._ranges[index-1] = (self._ranges[index-1][0], slice_stop,
                                     value)
            self._ranges.pop(index)

        # merge with next if same value
        if index < len(self._ranges) - 1 and self._ranges[index+1][2] == value:
            self._ranges[index] = (self._ranges[index][0],
                                   self._ranges[index+1][1], value)
            self._ranges.pop(index+1)

        # set the value in case missed elsewhere
        self._ranges[index] = (self._ranges[index][0],
                               self._ranges[index][1], value)

    def __setitem__(self, id, value):
        if isinstance(id, slice):
            # Get the start, stop, and step from the slice
            for ii in xrange(*id.indices(len(self))):
                self.set_data(ii, value)
        elif isinstance(id, int):
            if id < 0:  # Handle negative indices
                id += len(self)
            self.set_data(id, value)
        elif isinstance(id, (tuple, list)):
            for index in id:
                self.set_data(index, value)
        else:
            raise TypeError("Invalid argument type.")

    def __setslice__(self, start, stop, value):
        self.set_data_by_range(start, stop, value)

    def __iter__(self):
        return ListIterator(self)

    def __contains__(self, item):
        for (_, _, value) in self._ranges:
            if value == item:
                return True
        return False

    def count(self, x):
        result = 0
        for (start, stop, value) in self._ranges:
            if value == x:
                result = result + stop - start
        return result

    def index(self, x):
        for (start, _, value) in self._ranges:
            if value == x:
                return start
        raise ValueError("{} is not in list".format(x))

    def ranges(self):
        return list(self._ranges)

    def setdefault(self, default):
        self._default = default