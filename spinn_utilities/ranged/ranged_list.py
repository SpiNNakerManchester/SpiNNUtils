from spinn_utilities.ranged.abstract_list import AbstractList
from spinn_utilities.ranged.multiple_values_exception \
    import MultipleValuesException


class RangedList(AbstractList):

    def __init__(self, size, default, key=None):
        """
        Constructor for a ranged list.

        :param size: Fixed length of the list
        :param default: Default value to given to all elements in the list
        :param key: The dict key this list covers.
        This is used only for better Exception messages
        """
        AbstractList.__init__(self, size=size, key=key)
        self._default = default
        self._ranges = []
        self._ranges.append((0, size, default))

    def get_value_by_id(self, id):
        """
        Returns the value for one item in the list

        :param id: One of the ids of an element in the list
        :type id: int
        :return: The value of that element
        """
        self._check_id(id)
        for (start, stop, value) in self.iter_ranges():
            if id < stop:
                return value

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
        self._check_slice(slice_start, slice_stop)
        found_value = False
        result = None
        for (_start, _stop, _value) in self.iter_ranges():
            if slice_start < _stop:
                if found_value:
                    if result != _value:
                        raise MultipleValuesException(
                            self._key, result, _value)
                else:
                    result = _value
                    found_value = True
                if slice_stop <= _stop:
                    return _value

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
        result = self.get_value_by_id(ids[0])
        for id in ids[1:]:
            value = self.get_value_by_id(id)
            if result != value:
                raise MultipleValuesException(self._key, result, value)
        return result

    def iter_by_slice(self, slice_start, slice_stop):
        """
        Fast NOT update safe iterator of all elements in the slice

        Note: Duplicate/Repeated elements are yielded for each id

        :return: yields each element one by one
        """
        ranges = self.iter_ranges()
        current = ranges.next()
        while current[1] < slice_start:
            current = ranges.next()
        while current[0] < slice_stop:
            first = max(current[0], slice_start)
            end_point = min(current[1], slice_stop)
            for _ in range(end_point - first):
                yield current[2]
            current = ranges.next()

    def iter_ranges(self):
        """
        Fast NOT update safe iterator of the ranges

        :return: yields each range one by one
        """
        for r in self.get_ranges():
            yield r

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

    def set_value(self, value):
        """
        Sets ALL elements in the list to this value.

        Note Does not change the default

        :param value: new value
        """
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
                if id + 1 < stop:  # Need a new range after the id
                    self._ranges.insert(index + 1, (id + 1, stop, old_value))
                if id > start:   # Need a new range before the id
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
        while index < len(self._ranges) - 1 and \
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
        """
        Support for the list[x] == format

        :param id: A single Element id, the
        :param value:
        :return:
        """
        if isinstance(id, slice):
            # Get the start, stop, and step from the slice
            for ii in xrange(*id.indices(len(self))):
                self.set_value_by_id(ii, value)
        elif isinstance(id, int):
            if id < 0:  # Handle negative indices
                id += len(self)
            self.set_value_by_id(id, value)
        else:
            for index in id:
                self.set_value_by_id(index, value)

    def __setslice__(self, start, stop, value):
        self.set_value_by_slice(start, stop, value)

    def get_ranges(self):
        """
        Returns a copy of the list of ranges.

        As this is a copy it will not refelct any updates
        :return:
        """
        return list(self._ranges)

    def set_default(self, default):
        """
        Sets the default value

        NOTE: Does not change the value of any element in the list

        :param default: new default value
        """
        self._default = default

    def get_default(self):
        """
        Returns the default value for this list

        :return: Default Value
        """
        return self._default
