from spinn_utilities.lazy_range_dictionary.list_iterator import ListIterator


class LazyList(object):
    """
    A lazy implemantation of list.

    Functions that change the size of the list are NOT Supported.
    These include
        __setitem__ where key = len
        __delitem__
        append
        extend
        insert
        pop
        remove

    Function that manipulate the list based on values are not supported.
    These include
        reverse
        sort
    """

    def __init__(self, size, value):
        self._size = size
        self._ranges = []
        self._ranges.append((0, size - 1, value))

    def __len__(self):
        return self._size

    def get_data(self, key):
        if key < 0:
            raise IndexError(
                "The index {0!d} is out of range.".format(key))
        if key >= len(self):
            raise IndexError(
                "The index {0!d} is out of range.".format(key))
        for (start, stop, value) in self._ranges:
            if key <= stop:
                return value

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
        if key < 0:
            raise IndexError(
                "The index {0!d} is out of range.".format(key))
        if key >= len(self):
            raise IndexError(
                "The index {0!d} is out of range.".format(key))
        for index, (start, stop, old_value) in enumerate(self._ranges):
            if key <= stop:
                if value == old_value:
                    return  # alreay set as needed so do nothing
                self._ranges[index] = (key, key, value)
                if key < stop:  # Need a new range after the key
                    self._ranges.insert(index+1, (key + 1, stop, old_value))
                if key > start:   # Need a new range before the key
                    self._ranges.insert(index, (start, key - 1, old_value))
                if index > 0:
                    if self._ranges[index][2] == self._ranges[index-1][2]:
                        self._ranges[index - 1] = (
                            self._ranges[index - 1][0],
                            self._ranges[index][1],
                            self._ranges[index][2])
                        self._ranges.pop(index)
                if index < len(self._ranges) - 1:
                    if self._ranges[index][2] == self._ranges[index+1][2]:
                        self._ranges[index] = (
                            self._ranges[index][0],
                            self._ranges[index + 1][1],
                            self._ranges[index + 1][2])
                        self._ranges.pop(index + 1)
                return

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            # Get the start, stop, and step from the slice
            for ii in xrange(*key.indices(len(self))):
                self.set_data(ii, value)
        elif isinstance(key, int):
            if key < 0:  # Handle negative indices
                key += len(self)
            self.set_data(key, value)
        else:
            raise TypeError("Invalid argument type.")

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
                result = result + stop - start + 1
        return result

    def index(self, x):
        for (start, _, value) in self._ranges:
            if value == x:
                return start
        raise ValueError("{} is not in list".format(x))
