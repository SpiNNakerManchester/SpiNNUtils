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

# pylint: disable=redefined-builtin
from past.builtins import range, xrange
from six import raise_from
from spinn_utilities.overrides import overrides
from spinn_utilities.helpful_functions import is_singleton
from .abstract_list import AbstractList
from .multiple_values_exception import MultipleValuesException

import numpy


def function_iterator(function, size, ids=None):
    """ Converts a function into an iterator based on size or IDs.\
    This so that the function can be used to create a list as in::

        list(function_iterator(lambda x: x * 2 , 3, ids=[2, 4, 6]))

    :param function: A function with one integer parameter that returns a value
    :param size: The number of elements to put in the list. If used, the\
        function will be called with `range(size)`. Ignored if `ids` provided
    :param ids: A list of IDs to call the function for or None to use the size.
    :type ids: list of int
    :return: a list of values
    """
    if ids is None:
        ids = xrange(size)
    for _id in ids:
        yield function(_id)


class RangedList(AbstractList):
    """ A list that is able to efficiently hold large numbers of elements\
        that all have the same value.
    """
    __slots__ = [
        "_default", "_key", "_ranged_based", "_ranges"]

    def __init__(
            self, size=None, value=None, key=None, use_list_as_value=False):
        """
        :param size: Fixed length of the list
        :param value: value to given to all elements in the list
        :param key: The dict key this list covers.\
            This is used only for better Exception messages
        :param use_list_as_value: True if the value *is* a list
        """
        if size is None:
            try:
                size = len(value)
            except TypeError:
                raise ValueError("value parameter must have a length to "
                                 "determine the unsupplied size")
        AbstractList.__init__(self, size=size, key=key)
        if not use_list_as_value and not self.is_list(value, size):
            self._default = value
        self.set_value(value, use_list_as_value)

    @overrides(AbstractList.range_based)
    def range_based(self):
        return self._ranged_based

    @overrides(AbstractList.get_value_by_id)
    def get_value_by_id(self, id):  # @ReservedAssignment
        self._check_id_in_range(id)

        # If range based, find the range containing the value and return
        if self._ranged_based:
            for (_, stop, value) in self._ranges:
                if id < stop:
                    return value  # pragma: no cover

            # Must never get here because the ID is in range
            raise ValueError  # pragma: no cover

        # Non-range-based so just return the value
        return self._ranges[id]

    @overrides(AbstractList.get_single_value_by_slice)
    def get_single_value_by_slice(self, slice_start, slice_stop):
        slice_start, slice_stop = self._check_slice_in_range(
            slice_start, slice_stop)

        # If the list is formed of ranges...
        if self._ranged_based:
            found_value = False
            result = None

            # Go through the ranges until in range (assumed sorted)
            for (_, stop, value) in self._ranges:

                # If we have found a range in the slice
                if slice_start < stop:

                    # If we have already found a range in the slice, check the
                    # value is the same
                    if found_value:
                        if not numpy.array_equal(result, value):
                            raise MultipleValuesException(
                                self._key, result, value)

                    # If this is the first range in the slice, store it
                    else:
                        result = value
                        found_value = True

                    # If we have found a range that finishes outside of the
                    # slice, we have done, and can safely return the value
                    if slice_stop <= stop:
                        return value

            # This must be never possible, as the slices must be in range of
            # the list
            raise ValueError  # pragma: no cover

        # A non-range based list just has lots of single values, so check
        # they are all the same within the slice
        result = self._ranges[slice_start]
        for _value in self._ranges[slice_start+1: slice_stop]:
            if not numpy.array_equal(result, _value):
                raise MultipleValuesException(self._key, result, _value)
        return result

    @overrides(AbstractList.get_single_value_by_ids)
    def get_single_value_by_ids(self, ids):
        # Take the first ID, and then simply check all the others are the same
        # This works for both range-based and non-range-based
        result = self.get_value_by_id(ids[0])
        for id_value in ids[1:]:
            value = self.get_value_by_id(id_value)
            if not numpy.array_equal(result, value):
                raise MultipleValuesException(self._key, result, value)
        return result

    def __iter__(self):
        """ Fast but *not* update-safe iterator of all elements.

        .. note::
            Duplicate/Repeated elements are yielded for each ID.

        :return: yields each element one by one
        """
        if self._ranged_based:
            for (start, stop, value) in self._ranges:
                for _ in xrange(stop - start):
                    yield value
        else:
            for value in self._ranges:
                yield value

    @overrides(AbstractList.iter_by_slice)
    def iter_by_slice(self, slice_start, slice_stop):
        slice_start, slice_stop = self._check_slice_in_range(
            slice_start, slice_stop)

        # If range based, go through the ranges that intersect the slice
        if self._ranged_based:

            # Find the first range within the slice
            ranges = self.iter_ranges()
            (start, stop, value) = next(ranges)
            while stop < slice_start:
                (start, stop, value) = next(ranges)

            # Continue until outside of the slice
            while start < slice_stop:
                first = max(start, slice_start)
                end_point = min(stop, slice_stop)
                for _ in xrange(end_point - first):
                    yield value
                try:
                    (start, stop, value) = next(ranges)
                except StopIteration:
                    return
        # If non-range-based, just go through the values
        else:
            for value in self._ranges[slice_start: slice_stop]:
                yield value

    @overrides(AbstractList.iter_ranges)
    def iter_ranges(self):
        # If range based just yield the ranges
        if self._ranged_based:
            for r in self._ranges:
                yield r

        # If non-range based, build the ranges
        else:
            previous_value = self._ranges[0]
            previous_start = 0
            current_start = 0
            current_value = None
            for start, value in enumerate(self._ranges):
                current_start = start
                current_value = value
                if not numpy.array_equal(value, previous_value):
                    yield (previous_start, start, previous_value)
                    previous_start = start
                    previous_value = value
            yield (previous_start, current_start + 1, current_value)

    @overrides(AbstractList.iter_ranges_by_slice)
    def iter_ranges_by_slice(self, slice_start, slice_stop):
        slice_start, slice_stop = self._check_slice_in_range(
            slice_start, slice_stop)

        # If range-based, go through ranges that intersect the slice
        if self._ranged_based:
            for (start, stop, value) in self._ranges:
                if slice_start < stop:

                    # The range is updated so that the start and stop values
                    # are within the slice requested
                    yield (max(start, slice_start), min(stop, slice_stop),
                           value)
                    if slice_stop <= stop:
                        break

        # If non-range based, just go through the values
        else:
            previous_value = self._ranges[slice_start]
            previous_start = slice_start
            for index, value in \
                    enumerate(self._ranges[slice_start: slice_stop]):
                if not numpy.array_equal(value, previous_value):
                    # Index is one ahead so no need for a + 1 here
                    yield (previous_start, slice_start + index, previous_value)
                    previous_start = slice_start + index
                    previous_value = value
            yield (previous_start, slice_stop, previous_value)

    # pylint: disable=unused-argument
    @staticmethod
    def is_list(value, size):  # @UnusedVariable
        """ Determines if the value should be treated as a list.

        .. note::
            This method can be extended to add other checks for list in which\
            case :py:meth:`as_list` must also be extended.
        """

        # Assume any iterable is a list
        if callable(value):
            return True
        return not is_singleton(value)

    @staticmethod
    def as_list(value, size, ids=None):
        """ Converts (if required) the value into a list of a given size. \
            An exception is raised if value cannot be given size elements.

        .. note::
            This method can be extended to add other conversions to list in\
            which case :py:meth:`is_list` must also be extended.

        :param value:
        :return: value as a list
        :raises Exception: if the number of values and the size do not match
        """
        if callable(value):
            values = list(function_iterator(value, size, ids))
        else:
            values = list(value)
        if len(values) != size:
            raise Exception("The number of values does not equal the size")
        return values

    def set_value(self, value, use_list_as_value=False):
        """ Sets *all* elements in the list to this value.

        .. note::
            Does not change the default.

        :param value: new value
        :param use_list_as_value: True if the value to be set *is* a list
        """

        # If the value to set is a list, just copy the values
        if not use_list_as_value and self.is_list(value, self._size):
            self._ranges = self.as_list(value, self._size)
            self._ranged_based = False

        # Otherwise store the value directly assuming it is the same value
        # for all items
        else:
            self._ranges = []
            self._ranges.append((0, self._size, value))
            self._ranged_based = True

    def set_value_by_id(self, id, value):  # @ReservedAssignment
        """ Sets the value for a single ID to the new value.

        .. note::
            This method only works for a single positive int ID.\
            Use `set` or `__set__` for slices, tuples, lists and negative\
            indexes.

        :param id: Single ID
        :type id: int
        :param value: The value to save
        :type value: anything
        """
        self._check_id_in_range(id)

        # If non-range-based, set the value directly
        if not self._ranged_based:
            self._ranges[id] = value
            return

        # Find the range in which to set the value
        for index, (start, stop, old_value) in enumerate(self._ranges):
            if id < stop:

                # If already set as needed, do nothing
                if numpy.array_equal(value, old_value):
                    return

                # Split the ID out of the range
                self._ranges[index] = (id, id + 1, value)

                # Need a new range after the ID
                if id + 1 < stop:
                    self._ranges.insert(index + 1, (id + 1, stop, old_value))

                # Need a new range before the ID
                if id > start:
                    self._ranges.insert(index, (start, id, old_value))

                # If not at the last range, update the start and stop value of
                # the next range
                if index < len(self._ranges) - 1:
                    if numpy.array_equal(self._ranges[index][2],
                                         self._ranges[index + 1][2]):
                        self._ranges[index] = (
                            self._ranges[index][0],
                            self._ranges[index + 1][1],
                            self._ranges[index + 1][2])
                        self._ranges.pop(index + 1)

                # If not at the first range, update the start and stop value
                # of the first range
                if index > 0:
                    if numpy.array_equal(self._ranges[index][2],
                                         self._ranges[index - 1][2]):
                        self._ranges[index - 1] = (
                            self._ranges[index - 1][0],
                            self._ranges[index][1],
                            self._ranges[index][2])
                        self._ranges.pop(index)

                # We found it so stop
                return

    def set_value_by_slice(
            self, slice_start, slice_stop, value, use_list_as_value=False):
        """ Sets the value for a single range to the new value.

        .. note::
            This method only works for a single positive int ID.\
            Use `set` or `__set__` for slices, tuples, lists and negative\
            indexes.

        :param slice_start: Start of the range
        :type slice_start: int
        :param slice_stop: Exclusive end of the range
        :type slice_stop: int
        :param value: The value to save
        :type value: anything
        """
        slice_start, slice_stop = self._check_slice_in_range(
            slice_start, slice_stop)
        if (slice_start == slice_stop):
            return  # Empty list so do nothing

        # If the value to set is a list, set the values directly
        if not use_list_as_value and self.is_list(
                value, size=slice_stop - slice_start):
            return self._set_values_list(range(slice_start, slice_stop), value)

        # If non-ranged-based, set the values directly
        if not self._ranged_based:
            for id_value in xrange(slice_start, slice_stop):
                self._ranges[id_value] = value
            return

        # Skip ranges before start of slice
        index = 0
        while (index < len(self._ranges) - 1 and
               (self._ranges[index][1] <= slice_start)):
            index += 1

        # Strip off start of first range in case needed
        (_start, _stop, old_value) = self._ranges[index]

        # If the slice to set starts after the current range,
        # we may need a new range before the key
        if slice_start > _start:

            # If the values are different, add a new range with the old value
            if not numpy.array_equal(value, old_value):
                self._ranges.insert(index, (_start, slice_start, old_value))

                # We have added a value so move on one
                index += 1

                # Change start of old range but leave value for now
                self._ranges[index] = (slice_start, _stop, old_value)
                (_start, _stop, old_value) = self._ranges[index]

            # Existing already has this value so start the slice to set
            # at the start of this range
            else:
                slice_start = _start

        # Merge with next if overlaps with that one
        while slice_stop > _stop:
            (_start, _stop, old_value) = self._ranges.pop(index + 1)
            self._ranges[index] = (slice_start, _stop, old_value)

        # Split off end of merged range if required
        if slice_stop < _stop:
            self._ranges[index] = (slice_start, slice_stop, old_value)
            self._ranges.insert(index+1, (slice_stop, _stop, old_value))

        # merge with previous if same value
        if index > 0 and numpy.array_equal(self._ranges[index-1][2], value):
            self._ranges[index-1] = (self._ranges[index-1][0], slice_stop,
                                     value)
            self._ranges.pop(index)
            index -= 1

        # merge with next if same value
        if index < len(self._ranges) - 1 and numpy.array_equal(
                self._ranges[index+1][2],  value):
            self._ranges[index] = (self._ranges[index][0],
                                   self._ranges[index + 1][1], value)
            self._ranges.pop(index + 1)

        # set the value in case missed elsewhere
        self._ranges[index] = (self._ranges[index][0],
                               self._ranges[index][1], value)

    def _set_values_list(self, ids, value):
        values = self.as_list(value=value, size=len(ids), ids=ids)
        for id_value, val in zip(ids, values):
            self.set_value_by_id(id_value, val)

    def set_value_by_ids(self, ids, value, use_list_as_value=False):
        if not use_list_as_value and self.is_list(value, len(ids)):
            self._set_values_list(ids, value)
        else:
            for id_value in ids:
                self.set_value_by_id(id_value, value)

    def set_value_by_selector(self, selector, value, use_list_as_value=False):
        """ Support for the `list[x] =` format.

        :param id: A single ID, a slice of IDs or a list of IDs
        :param value:
        """

        # Handle a slice
        if isinstance(selector, slice):
            if selector.step is None or selector.step == 1:
                (start, stop, _) = selector.indices(self._size)
                self.set_value_by_slice(start, stop, value, use_list_as_value)
                return

        ids = self.selector_to_ids(selector)
        self.set_value_by_ids(
            ids=ids, value=value, use_list_as_value=use_list_as_value)

    __setitem__ = set_value_by_selector

    def get_ranges(self):
        """ Returns a copy of the list of ranges.

        .. note::
            As this is a copy it will not reflect any updates.

        :return:
        """
        if self._ranged_based:
            return list(self._ranges)
        return list(self.iter_ranges())

    def set_default(self, default):
        """ Sets the default value.

        .. note::
            Does not change the value of any element in the list.

        :param default: new default value
        """
        self._default = default

    @overrides(AbstractList.get_default, extend_doc=False)
    def get_default(self):
        """ Returns the default value for this list.

        :return: Default Value
        """
        try:
            return self._default
        except AttributeError as e:
            raise_from(Exception("Default value not set."), e)
