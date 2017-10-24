from spinn_utilities.ranged.list_iterator import ListIterator
from spinn_utilities.ranged.multiple_values_exception \
    import MultipleValuesException


class RangedList(object):
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
    """

    def __init__(self, size, default, key=None):
        self._size = size
        self._default = default
        self._ranges = []
        self._ranges.append((0, size, default))
        self._key=key

    def __len__(self):
        return self._size

    def get_value_all(self):
        if len(self._ranges) > 1:
            raise MultipleValuesException(self._key, self._ranges[0][2],
                                          self._ranges[1][2])
        return self._ranges[0][2]

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
        if (slice_start > slice_stop and not slice_start is None
                and not slice_stop is None):
            if not isinstance(slice_start, int):
                raise TypeError("Invalid argument type {}."
                                "".format(type(slice_start)))
            if not isinstance(slice_stop, int):
                raise TypeError("Invalid argument type {}."
                                "".format(type(slice_start)))
            raise IndexError(
                "The range_start {0!d} is after the range stop {0!d}."
                "".format(slice_start, slice_stop))
        if slice_start < 0 and not slice_start is None:
            if isinstance(slice_start, int):
                raise IndexError(
                    "The range_start {0!d} is out of range."
                    "".format(slice_start))
            raise TypeError("Invalid argument type {}."
                            "".format(type(slice_start)))
        if slice_stop > len(self) and not slice_stop is None:
            if isinstance(slice_stop, int):
                raise IndexError(
                    "The range_stop {0!d} is out of range."
                    "".format(slice_stop))
            raise TypeError("Invalid argument type {}."
                            "".format(type(slice_stop)))

    def get_value_by_id(self, id):
        self._check_id(id)
        for (start, stop, value) in self._ranges:
            if id < stop:
                return value

    def get_value_by_slice(self, slice_start, slice_stop):
        self._check_slice(slice_start, slice_stop)
        result = None
        for (_start, _stop, _value) in self._ranges:
            if slice_start < _stop:
                if result is None:
                    result = _value
                elif result != _value:
                    raise MultipleValuesException(self._key, result, _value)
                if slice_stop <= _stop:
                    return _value

    def __getslice__(self, start, stop):
        return self.get_value_by_slice(start, stop)

    def get_value_by_ids(self, ids):
        result = self.get_value_by_id(ids[0])
        for id in ids[1:]:
            value = self.get_value_by_id(id)
            if result != value:
                raise MultipleValuesException(self._key, result, value)
        return result

    def __getitem__(self, key):
        if isinstance(key, slice):
            # Get the start, stop, and step from the slice
            return [self[ii] for ii in xrange(*key.indices(self._size))]
        elif isinstance(key, int):
            if key < 0:  # Handle negative indices
                key += len(self)
            return self.get_value_by_id(key)
        else:
            raise TypeError("Invalid argument type.")

    def set_value(self, value):
        self._ranges = []
        self._ranges.append((0, self._size, value))

    def set_value_by_id(self, id, value):
        """
        Sets the value for a single id to the new value.

        Note: This method only works for a single possitive int id.
        use set or __set__ for slices, tuples, lists and negative indexes
        :param id: Single id
        :type id:int
        :param value:  The value to save
        :type value: anything
        """
        self._check_id(id)
        for index, (start, stop, old_value) in enumerate(self._ranges):
            if id < stop:
                if value == old_value:
                    return  # alreay set as needed so do nothing
                self._ranges[index] = (id, id + 1, value)
                if id +1 < stop:  # Need a new range after the key
                    self._ranges.insert(index + 1, (id + 1, stop, old_value))
                if id > start:   # Need a new range before the key
                    self._ranges.insert(index, (start, id, old_value))
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

    def set_value_by_slice(self, slice_start, slice_stop, value):
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
        self._check_slice(slice_start, slice_stop)
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
                self.set_value_by_id(ii, value)
        elif isinstance(id, int):
            if id < 0:  # Handle negative indices
                id += len(self)
            self.set_value_by_id(id, value)
        elif isinstance(id, (tuple, list)):
            for index in id:
                self.set_value_by_id(index, value)
        else:
            raise TypeError("Invalid argument type.")

    def __setslice__(self, start, stop, value):
        self.set_value_by_slice(start, stop, value)

    def iter_by_ids(self, ids):
        range_pointer = 0
        for id in ids:
            # check if ranges reset so too far ahead
            if id < self._ranges[range_pointer][0]:
                range_pointer = 0
                while id > self._ranges[range_pointer][0]:
                    range_pointer += 1
            # check if pointer needs to move on
            while id >= self._ranges[range_pointer][1]:
                range_pointer += 1
            yield self._ranges[range_pointer][2]

    def iter(self):
        return self.iter_by_ids(range(self._size))

    def __iter__(self):
        for (start, stop, value) in self._ranges:
            for x in range(stop - start):
                yield value

    def slice_iter(self, slice_start, slice_stop):
        for (start, stop, value) in self._ranges:
            if slice_start < stop and slice_stop >= start:
                first = max(start, slice_start)
                end_point = min(stop, slice_stop)
                for _ in range(end_point - first):
                    yield value

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

    def iter_ranges(self):
        return iter(self._ranges)

    def get_ranges(self):
        return list(self._ranges)

    def iter_ranges_by_id(self, id):
        self._check_id(id)
        for (start, stop, value) in self._ranges:
            if id < stop:
                yield (id, id + 1, value)
                break

    def iter_ranges_by_slice(self, slice_start, slice_stop):
        self._check_slice(slice_start, slice_stop)
        for (_start, _stop, value) in self._ranges:
            if slice_start < _stop:
                yield (max(_start, slice_start), min(_stop, slice_stop),
                       value)
                if slice_stop <= _stop:
                    break

    def iter_ranges_by_ids(self, ids):
        range_pointer = 0
        result = None
        for id in ids:
            # check if ranges reset so too far ahead
            if id < self._ranges[range_pointer][0]:
                range_pointer = 0
                while id > self._ranges[range_pointer][0]:
                    range_pointer += 1
            # check if pointer needs to move on
            while id >= self._ranges[range_pointer][1]:
                range_pointer += 1
            if not result is None:
                if (result[1] == id and
                            result[2] == self._ranges[range_pointer][2]):
                    result = (result[0], id + 1, result[2])
                    continue
                yield result
            result = (id, id + 1, self._ranges[range_pointer][2])
        yield result

    def setdefault(self, default):
        self._default = default

