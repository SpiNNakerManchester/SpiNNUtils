# Copyright (c) 2017 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations
from typing import (
    Any, Callable, Generic, List, Iterable, Iterator, Optional, Sequence,
    Sized, Tuple, Union, cast, final)
from typing_extensions import TypeAlias, TypeGuard
from spinn_utilities.overrides import overrides
from spinn_utilities.helpful_functions import is_singleton
from .abstract_sized import Selector
from .abstract_list import AbstractList, T, _eq, IdsType
from .multiple_values_exception import MultipleValuesException

#: The type of a range descriptor
_RangeType: TypeAlias = Tuple[int, int, T]
# The type of things we consider to be a list of values
_ListType: TypeAlias = Union[Callable[[int], T], Sequence[T]]
# The type of value arguments in several places
_ValueType: TypeAlias = Optional[Union[T, _ListType]]


def function_iterator(
        function: Callable[[int], T], size: int,
        ids: Optional[Iterable[int]] = None) -> Iterable[T]:
    """
    Converts a function into an iterator based on size or IDs.
    This so that the function can be used to create a list as in::

        list(function_iterator(lambda x: x * 2 , 3, ids=[2, 4, 6]))

    :param ~collections.abc.Callable[[int],object] function:
        A function with one integer parameter that returns a value
    :param int size:
        The number of elements to put in the list. If used, the function will
        be called with ``range(size)``. Ignored if ``ids`` provided
    :param ~collections.abc.Iterable(int) ids:
        A list of IDs to call the function for or ``None`` to use the size.
    :return: a sequence of values returned by the function
    :rtype: ~collections.abc.Iterable(object)
    """
    if ids is None:
        ids = range(size)
    for _id in ids:
        yield function(_id)


class RangedList(AbstractList[T], Generic[T]):
    """
    A list that is able to efficiently hold large numbers of elements
    that all have the same value.
    """
    __slots__ = [
        "_default", "_ranged_based", "_ranges"]

    def __init__(
            self, size: Optional[int] = None, value: _ValueType = None,
            key=None, use_list_as_value=False):
        """
        :param size:
            Fixed length of the list;
            if ``None``, the value must be a sized object.
        :type size: int or None
        :param value: value to given to all elements in the list
        :type value: object or ~collections.abc.Sized
        :param key: The dict key this list covers.
            This is used only for better Exception messages
        :param bool use_list_as_value: True if the value *is* a list
        """
        if size is None:
            try:
                size = len(value)  # type: ignore[arg-type]
            except TypeError as e:
                raise ValueError("value parameter must have a length to "
                                 "determine the unsupplied size") from e
        super().__init__(size=size, key=key)
        if not use_list_as_value and (
                not self.is_list(value, size) or self.__length(value) != size):
            self._default: Optional[T] = cast(Optional[T], value)
        else:
            self._default = None
        self._ranges: Union[List[T], List[_RangeType]]
        self._ranged_based: Optional[bool] = None
        self.set_value(value, use_list_as_value=use_list_as_value)

    def __length(self, value: Any) -> int:
        if callable(value):
            return self._size
        if not isinstance(value, Sized):
            return 1
        return len(value)

    @overrides(AbstractList.range_based)
    def range_based(self) -> bool:
        return self._ranged_based or False

    @property
    def __the_ranges(self) -> List[_RangeType]:
        assert self._ranged_based
        return cast(List[_RangeType], self._ranges)

    @property
    def __the_values(self) -> List[T]:
        assert not self._ranged_based
        return cast(List[T], self._ranges)

    @overrides(AbstractList.get_value_by_id)
    def get_value_by_id(self, the_id: int) -> T:
        the_id = self._check_id_in_range(the_id)

        # If range based, find the range containing the value and return
        if self._ranged_based:
            for (_, stop, value) in self.__the_ranges:
                if the_id < stop:
                    return value  # pragma: no cover

            # Must never get here because the ID is in range
            raise ValueError  # pragma: no cover

        # Non-range-based so just return the value
        return self.__the_values[the_id]

    @overrides(AbstractList.get_single_value_by_slice)
    def get_single_value_by_slice(
            self, slice_start: int, slice_stop: int) -> T:
        slice_start, slice_stop = self._check_slice_in_range(
            slice_start, slice_stop)

        # If the list is formed of ranges...
        if self._ranged_based:
            found_value = False
            result = None

            # Go through the ranges until in range (assumed sorted)
            for (_, stop, value) in self.__the_ranges:

                # If we have found a range in the slice
                if slice_start < stop:

                    # If we have already found a range in the slice, check the
                    # value is the same
                    if found_value:
                        if not _eq(result, value):
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
        result = self.__the_values[slice_start]
        for value in self.__the_values[slice_start+1: slice_stop]:
            if not _eq(result, value):
                raise MultipleValuesException(self._key, result, value)
        return result

    @overrides(AbstractList.get_single_value_by_ids)
    def get_single_value_by_ids(self, ids: IdsType) -> T:
        # Take the first ID, and then simply check all the others are the same
        # This works for both range-based and non-range-based
        result = self.get_value_by_id(ids[0])
        for id_value in ids[1:]:
            value = self.get_value_by_id(id_value)
            if not _eq(result, value):
                raise MultipleValuesException(self._key, result, value)
        return result

    def __iter__(self) -> Iterator[T]:
        """
        Fast but *not* update-safe iterator of all elements.

        .. note::
            Duplicate/Repeated elements are yielded for each ID.

        :return: yields each element one by one
        """
        if self._ranged_based:
            for (start, stop, value) in self.__the_ranges:
                for _ in range(stop - start):
                    yield value
        else:
            for value in self.__the_values:
                yield value

    @overrides(AbstractList.iter_by_slice)
    def iter_by_slice(self, slice_start: int, slice_stop: int) -> Iterator[T]:
        slice_start, slice_stop = self._check_slice_in_range(
            slice_start, slice_stop)

        # If non-range-based, just go through the values
        if not self._ranged_based:
            yield from self.__the_values[slice_start: slice_stop]
            return

        # Range-based, so go through the ranges that intersect the slice

        # Find the first range within the slice
        ranges = self.iter_ranges()
        (start, stop, value) = next(ranges)
        while stop < slice_start:
            (start, stop, value) = next(ranges)

        # Continue until outside of the slice
        while start < slice_stop:
            first = max(start, slice_start)
            end_point = min(stop, slice_stop)
            for _ in range(end_point - first):
                yield value
            try:
                (start, stop, value) = next(ranges)
            except StopIteration:
                return

    @overrides(AbstractList.iter_ranges)
    def iter_ranges(self) -> Iterator[_RangeType]:
        # If range based just yield the ranges
        if self._ranged_based:
            yield from self.__the_ranges
            return

        # If non-range based, build the ranges
        previous_value = self.__the_values[0]
        previous_start = 0
        current_start = 0
        current_value = None
        any_value = False
        for start, value in enumerate(self.__the_values):
            current_start = start
            current_value = value
            if not _eq(value, previous_value):
                yield (previous_start, start, previous_value)
                previous_start = start
                previous_value = value
            any_value = True
        if any_value:
            yield (previous_start, current_start + 1, cast(T, current_value))

    @overrides(AbstractList.iter_ranges_by_slice)
    def iter_ranges_by_slice(
            self, slice_start: int, slice_stop: int) -> Iterator[_RangeType]:
        slice_start, slice_stop = self._check_slice_in_range(
            slice_start, slice_stop)

        # If range-based, go through ranges that intersect the slice
        if self._ranged_based:
            for (start, stop, value) in self.__the_ranges:
                if slice_start < stop:

                    # The range is updated so that the start and stop values
                    # are within the slice requested
                    yield (max(start, slice_start), min(stop, slice_stop),
                           value)
                    if slice_stop <= stop:
                        break
            return

        # If non-range based, just go through the values
        previous_value = self.__the_values[slice_start]
        previous_start = slice_start
        for index, value in enumerate(
                self.__the_values[slice_start: slice_stop]):
            if not _eq(value, previous_value):
                # Index is one ahead so no need for a + 1 here
                yield (previous_start, slice_start + index, previous_value)
                previous_start = slice_start + index
                previous_value = value
        yield (previous_start, slice_stop, previous_value)

    # pylint: disable=unused-argument
    @final
    def is_list(self, value: _ValueType,
                size: Optional[int]) -> TypeGuard[_ListType]:
        """
        Determines if the value should be treated as a list.

        :param value: The value to examine.
        """
        return self.listness_check(value)

    def listness_check(self, value: _ValueType) -> bool:
        """
        Easier to override in subclasses as not type guard.

        .. note::
            This method can be extended to add other checks for list in which
            case :py:meth:`as_list` must also be extended.

        :param value: The value to examine.
        """
        # Assume any iterable is a list
        if callable(value):
            return True
        return not is_singleton(value)

    def as_list(
            self, value: _ListType, size: int,
            ids: Optional[IdsType] = None) -> List[T]:
        """
        Converts (if required) the value into a list of a given size.
        An exception is raised if value cannot be given size elements.

        .. note::
            This method can be extended to add other conversions to list in
            which case :py:meth:`listness_check` must also be extended.

        :param value:
        :return: value as a list
        :raises Exception: if the number of values and the size do not match
        """
        if callable(value):
            values = list(function_iterator(value, size, ids))
        else:
            values = list(value)
        if len(values) != size:
            raise ValueError(f"The number of values:{len(values)} "
                             f"does not equal the size:{size}")
        return values

    def set_value(self, value: _ValueType, use_list_as_value=False):
        """
        Sets *all* elements in the list to this value.

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
            self._ranges = [(0, self._size, value)]
            self._ranged_based = True

    def set_value_by_id(self, the_id: int, value: T):
        """
        Sets the value for a single ID to the new value.

        .. note::
            This method only works for a single positive int ID.
            Use ``set`` or ``__set__`` for slices, tuples, lists and negative
            indexes.

        :param int the_id: Single ID
        :param object value: The value to save
        """
        the_id = self._check_id_in_range(the_id)

        # If non-range-based, set the value directly
        if not self._ranged_based:
            self.__the_values[the_id] = value
            return

        # Find the range in which to set the value
        for idx, (start, stop, old_value) in enumerate(self.__the_ranges):
            if the_id < stop:
                break
        else:
            return

        # If already set as needed, do nothing
        if _eq(value, old_value):
            return

        ranges = self.__the_ranges

        # Split the ID out of the range
        ranges[idx] = (the_id, the_id + 1, value)

        # Need a new range after the ID
        if the_id + 1 < stop:
            ranges.insert(idx + 1, (the_id + 1, stop, old_value))

        # Need a new range before the ID
        if the_id > start:
            ranges.insert(idx, (start, the_id, old_value))

        # If not at the last range, update the start and stop value of
        # the next range
        if idx < len(ranges) - 1:
            if _eq(ranges[idx][2], ranges[idx + 1][2]):
                ranges[idx] = (
                    ranges[idx][0], ranges[idx + 1][1], ranges[idx + 1][2])
                ranges.pop(idx + 1)

        # If not at the first range, update the start and stop value
        # of the first range
        if idx > 0:
            if _eq(ranges[idx][2], ranges[idx - 1][2]):
                ranges[idx - 1] = (
                    ranges[idx - 1][0], ranges[idx][1], ranges[idx][2])
                ranges.pop(idx)

    def set_value_by_slice(
            self, slice_start: int, slice_stop: int, value: _ValueType,
            use_list_as_value=False):
        """
        Sets the value for a single range to the new value.

        .. note::
            This method only works for a single positive range.
            Use ``set`` or ``__set__`` for slices, tuples, lists and negative
            indexes.

        :param int slice_start: Start of the range
        :param int slice_stop: Exclusive end of the range
        :param object value: The value to save
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
            for id_value in range(slice_start, slice_stop):
                self.__the_values[id_value] = cast(T, value)
            return

        # Skip ranges before start of slice
        ranges = self.__the_ranges
        index = 0
        while index < len(ranges) - 1 and ranges[index][1] <= slice_start:
            index += 1

        # Strip off start of first range in case needed
        (_start, _stop, old_value) = ranges[index]

        # If the slice to set starts after the current range,
        # we may need a new range before the key
        if slice_start > _start:

            # If the values are different, add a new range with the old value
            if not _eq(value, old_value):
                ranges.insert(index, (_start, slice_start, old_value))

                # We have added a value so move on one
                index += 1

                # Change start of old range but leave value for now
                ranges[index] = (slice_start, _stop, old_value)
                (_start, _stop, old_value) = ranges[index]

            # Existing already has this value so start the slice to set
            # at the start of this range
            else:
                slice_start = _start

        # Merge with next if overlaps with that one
        while slice_stop > _stop:
            (_start, _stop, old_value) = ranges.pop(index + 1)
            ranges[index] = (slice_start, _stop, old_value)

        # Split off end of merged range if required
        if slice_stop < _stop:
            ranges[index] = (slice_start, slice_stop, old_value)
            ranges.insert(index+1, (slice_stop, _stop, old_value))

        # merge with previous if same value
        if index > 0 and _eq(ranges[index-1][2], value):
            ranges[index-1] = (ranges[index-1][0], slice_stop, value)
            ranges.pop(index)
            index -= 1

        # merge with next if same value
        if index < len(ranges) - 1 and _eq(ranges[index+1][2], value):
            ranges[index] = (ranges[index][0], ranges[index + 1][1], value)
            ranges.pop(index + 1)

        # set the value in case missed elsewhere
        ranges[index] = (ranges[index][0], ranges[index][1], value)

    def _set_values_list(self, ids: IdsType, value: _ListType):
        values = self.as_list(value=value, size=len(ids), ids=ids)
        for id_value, val in zip(ids, values):
            self.set_value_by_id(id_value, val)

    def set_value_by_ids(
            self, ids: IdsType, value: _ValueType, use_list_as_value=False):
        if not use_list_as_value and self.is_list(value, len(ids)):
            self._set_values_list(ids, value)
        else:
            for id_value in ids:
                self.set_value_by_id(id_value, cast(T, value))

    def set_value_by_selector(
            self, selector: Selector, value: _ValueType,
            use_list_as_value=False):
        """
        Support for the ``list[x] =`` format.

        :param selector: A single ID, a slice of IDs or a list of IDs
        :type selector: int or slice or list(int)
        :param object value:
        """
        if selector is None:
            self.set_value(value, use_list_as_value=use_list_as_value)
            return
        if isinstance(selector, slice):
            # Handle a slice
            if selector.step is None or selector.step == 1:
                (start, stop, _) = selector.indices(self._size)
                self.set_value_by_slice(
                    start, stop, value, use_list_as_value=use_list_as_value)
                return

        ids = self.selector_to_ids(selector)
        self.set_value_by_ids(
            ids=ids, value=value, use_list_as_value=use_list_as_value)

    __setitem__ = set_value_by_selector

    def get_ranges(self) -> List[_RangeType]:
        """
        Returns a copy of the list of ranges.

        .. note::
            As this is a copy it will not reflect any updates.

        :rtype: list(tuple(int,int,object))
        """
        if self._ranged_based:
            return list(self.__the_ranges)
        return list(self.iter_ranges())

    def set_default(self, default: Optional[T]):
        """
        Sets the default value.

        .. note::
            Does not change the value of any element in the list.

        :param object default: new default value
        """
        self._default = default

    @overrides(AbstractList.get_default, extend_doc=False)
    def get_default(self) -> Optional[T]:
        """
        Returns the default value for this list.

        :return: Default Value
        :rtype: object
        """
        try:
            return self._default
        except AttributeError as e:
            raise AttributeError("Default value not set.") from e

    def copy_into(self, other: RangedList[T]):
        """
        Turns this List into a of the other list but keep its ID.

        Depth is just enough so that any changes done through the RangedList
        API on other will not change self

        :param RangedList other: Another Ranged List to copy the values from
        """
        # Assume the _default and key remain unchanged
        self._ranged_based = other.range_based()
        # clear the list fast and 2.7 safe
        self._ranges *= 0
        if self._ranged_based:
            self.__the_ranges.extend(other.iter_ranges())
        else:
            self.__the_values.extend(other)

    def copy(self) -> RangedList[T]:
        """
        Creates a copy of this list.

        Depth is just enough so that any changes done through the RangedList
        API on other will not change self

        :return: The copy
        :rtype: RangedList
        """
        clone: RangedList[T] = RangedList(
            self._size, self._default, self._key)
        clone.copy_into(self)
        return clone
