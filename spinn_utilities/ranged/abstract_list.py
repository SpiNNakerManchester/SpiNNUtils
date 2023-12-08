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
from numbers import Number
import numpy
from numpy.typing import NDArray
from typing import (
    Any, Callable, Generic, Iterator, Optional, Sequence, Tuple,
    TypeVar, Union, cast)
from typing_extensions import TypeGuard
from typing_extensions import Self, TypeAlias
from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from spinn_utilities.overrides import overrides
from .abstract_sized import AbstractSized, Selector
from .multiple_values_exception import MultipleValuesException
#: :meta private:
ResultType = TypeVar("ResultType")
#: :meta private:
T = TypeVar("T")
#: :meta private:
U = TypeVar("U")
#: :meta private:
IdsType: TypeAlias = Union[Sequence[int], NDArray[numpy.integer]]


def _eq(x: Any, y: Any) -> bool:
    # Lies!
    return numpy.array_equal(cast(float, x), cast(float, y))


def _is_zero(value: Any) -> bool:
    return bool(numpy.isin(0, value))


def is_number(value: T) -> TypeGuard[float]:
    """
    Is the Value a simple integer or float?
    """
    return isinstance(value, Number)


class AbstractList(AbstractSized, Generic[T], metaclass=AbstractBase):
    """
    A ranged implementation of list.

    Functions that change the size of the list are *not* supported.
    These include::

        `__setitem__` where `key` >= `len`
        `__delitem__`
        `append`
        `extend`
        `insert`
        `pop`
        `remove`

    Function that manipulate the list based on values are not supported.
    These include::

        `reverse`, `__reversed__`
        `sort`

    In the current version the IDs are zero-based consecutive numbers so there
    is no difference between value-based IDs and index-based IDs,
    but this could change in the future.

    Supports the following arithmetic operations over the list:

    `+`
        element-wise addition or addition of a single scalar
    `-`
        element-wise subtraction or subtraction of a single scalar
    `*`
        element-wise multiplication or multiplication by a single scalar
    `/`
        element-wise true division or true division by a single scalar
    `//`
        element-wise floor division or floor division by a single scalar
    """
    __slots__ = ("_key", )

    def __init__(self, size: int, key=None):
        """
        :param int size: Fixed length of the list
        :param key: The dict key this list covers.
            This is used only for better Exception messages
        """
        super().__init__(size)
        self._key = key

    @abstractmethod
    def range_based(self) -> bool:
        """
        Shows if the list is suited to deal with ranges or not.

        All list must implement all the range functions,
        but there are times when using ranges will probably be slower than
        using individual values.
        For example the individual values may be stored in a list in which
        case the ranges are created on demand.

        :return: True if and only if Ranged based calls are recommended.
        :rtype: bool
        """
        raise NotImplementedError

    def __len__(self) -> int:
        """
        Size of the list, irrespective of actual values

        :return: the initial and Fixed size of the list
        """
        return self._size

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, AbstractList):
            if self.range_based() and other.range_based():
                return _eq(list(self.iter_ranges()),
                           list(other.iter_ranges()))
        return _eq(list(self), list(other))

    def __ne__(self, other: Any) -> bool:
        if not isinstance(other, AbstractList):
            return True
        return not self.__eq__(other)

    def __str__(self) -> str:
        return str(list(self))

    __repr__ = __str__

    def get_single_value_all(self) -> T:
        """
        If possible, returns a single value shared by the whole list.

        For multiple values use ``for x in list``, ``iter(list)`` or
        ``list.iter``, or one of the ``iter_ranges`` methods

        :return: Value shared by all elements in the list
        :raises ~spinn_utilities.ranged.MultipleValuesException:
            If even one elements has a different value
        """
        # This is not elegant code but as the ranges could be created on the
        # fly the best way.
        only_range: Optional[Tuple[int, int, T]] = None
        for this_range in self.iter_ranges():
            if only_range is not None:
                # If we can get another range, there must be more than one
                # value, so raise the exception
                raise MultipleValuesException(
                    self._key, only_range[2], this_range[2])
            only_range = this_range
        if only_range is None:
            # Pretend we totally failed
            raise StopIteration()
        # There isn't another range, so return the value from the only range
        return only_range[2]

    @abstractmethod
    def get_value_by_id(self, the_id: int) -> T:
        """
        Returns the value for one item in the list.

        :param the_id: One of the IDs of an element in the list
        :type the_id: int
        :return: The value of that element
        """
        raise NotImplementedError

    @abstractmethod
    def get_single_value_by_slice(
            self, slice_start: int, slice_stop: int) -> T:
        """
        If possible, returns a single value shared by the whole slice list.

        For multiple values, use ``for x in list``, ``iter(list)``,
        ``list.iter``, or one of the ``iter_ranges`` methods

        :return: Value shared by all elements in the slice
        :raises ~spinn_utilities.ranged.MultipleValuesException:
            If even one elements has a different value.
            Not thrown if elements outside of the slice have a different value
        """
        raise NotImplementedError

    def __getslice__(self, start: int, stop: int) -> Sequence[T]:
        return list(self.iter_by_slice(start, stop))

    @abstractmethod
    def get_single_value_by_ids(self, ids: IdsType) -> T:
        """
        If possible, returns a single value shared by all the IDs.

        For multiple values, use ``for x in list``, ``iter(list)``,
        ``list.iter``, or one of the ``iter_ranges`` methods.

        :return: Value shared by all elements with these IDs
        :raises ~spinn_utilities.ranged.MultipleValuesException:
            If even one elements has a different value.
            Not thrown if elements outside of the IDs have a different value,
            even if these elements are between the ones pointed to by IDs
        """
        raise NotImplementedError

    def __getitem__(self, selector: Selector) -> Union[Self, T, Sequence[T]]:
        """
        Supports the `list[x]` to return an element or slice of the list.

        :param selector: The int ID, slice
        :return: The element[key] or the slice
        """

        if selector is None:
            return self

        # If the key is a slice, get the values from the slice
        if isinstance(selector, slice):

            # If the slice is continuous, use the continuous slice getter
            if selector.step is None or selector.step == 1:
                return list(self.iter_by_slice(
                    slice_start=selector.start, slice_stop=selector.stop))

            # Otherwise get the items one by one using the start, stop, and
            # step from the slice
            return [
                cast(T, self[i])
                for i in range(*selector.indices(self._size))]

        # If the key is an int, get the single value
        elif self._is_id_type(selector):
            selector = int(cast(int, selector))

            # Handle negative indices
            if selector < 0:
                selector += len(self)
            return self.get_value_by_id(selector)
        else:
            return [self.get_value_by_id(i)
                    for i in cast(Sequence[int], selector)]

    def iter_by_id(self, the_id: int) -> Iterator[T]:
        """
        Fast but *not* update-safe iterator by one ID.

        While ``next`` can only be called once, this is an iterator so it can
        be mixed in with other iterators.

        :param the_id: ID
        :return: yields the elements
        """
        yield self.get_value_by_id(the_id)

    def iter_by_ids(self, ids: IdsType) -> Iterator[T]:
        """
        Fast but *not* update-safe iterator by collection of IDs.

        .. note::
            Duplicate/Repeated elements are yielded for each ID.

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

            # Move on until the ID is in range
            while id_value >= stop:
                (_, stop, value) = next(ranges)

            yield value

    def iter(self) -> Iterator[T]:
        """
        Update-safe iterator of all elements.

        .. note::
            Duplicate/Repeated elements are yielded for each ID

        :return: yields each element one by one
        """
        for id_value in range(self._size):
            yield self.get_value_by_id(id_value)

    def __iter__(self) -> Iterator[T]:
        """
        Fast but *not* update-safe iterator of all elements.

        .. note::
            Duplicate/Repeated elements are yielded for each ID

        :return: yields each element one by one
        """
        try:
            if self.range_based():
                for (start, stop, value) in self.iter_ranges():
                    for _ in range(stop - start):
                        yield value
            else:
                for id_value in range(self._size):
                    yield self.get_value_by_id(id_value)
        except StopIteration:
            return

    def iter_by_slice(self, slice_start: int, slice_stop: int) -> Iterator[T]:
        """
        Fast but *not* update-safe iterator of all elements in the slice.

        .. note::
            Duplicate/Repeated elements are yielded for each ID

        :return: yields each element one by one
        """
        slice_start, slice_stop = self._check_slice_in_range(
            slice_start, slice_stop)
        if self.range_based():
            for (start, stop, value) in \
                    self.iter_ranges_by_slice(slice_start, slice_stop):
                for _ in range(start, stop):
                    yield value
        else:
            for id_value in range(slice_start, slice_stop):
                yield self.get_value_by_id(id_value)

    def iter_by_selector(self, selector: Selector = None) -> Iterator[T]:
        """
        Fast but *not* update-safe iterator of all elements in the slice.

        :param selector: See :py:meth:`AbstractSized.selector_to_ids`
        :return: yields the selected elements one by one
        """
        # No Selector so iter all fast
        if selector is None:
            return self.__iter__()

        if isinstance(selector, int):
            # Handle negative indices
            if selector < 0:
                selector += len(self)
            return self.iter_by_id(selector)

        # If the key is a slice, get the values from the slice
        if isinstance(selector, slice):

            # If the slice is continuous, use the continuous slice getter
            if selector.step is None or selector.step == 1:
                return self.iter_by_slice(selector.start, selector.stop)
            else:
                (slice_start, slice_stop, step) = selector.indices(self._size)
                return self.iter_by_ids(range(slice_start, slice_stop, step))

        ids = self.selector_to_ids(selector)
        return self.iter_by_ids(ids)

    def get_values(self, selector: Selector = None) -> Sequence[T]:
        """
        Get the value all elements pointed to the selector.

        .. note::
            Unlike ``__get_item__`` this method always returns a list even
            if the selector is a single int.

        :param selector: See :py:meth:`AbstractSized.selector_to_ids`
        :return: returns a list if the item which may be empty or have only
            single value
        :rtype: list
        """
        return list(self.iter_by_selector(selector))

    def __contains__(self, item: T) -> bool:
        return any(_eq(value, item)
                   for (_, _, value) in self.iter_ranges())

    def count(self, x: T) -> int:
        """
        Counts the number of elements in the list with value ``x``.

        :param x:
        :return: count of matching elements
        :rtype: int
        """
        return sum(
            stop - start
            for (start, stop, value) in self.iter_ranges()
            if _eq(value, x))

    def index(self, x: T) -> int:
        """
        Finds the first ID of the first element in the list with the given
        value.

        :param x: The value to find.
        :return: The ID/index
        :raise ValueError: If the value is not found
        """
        for (start, _, value) in self.iter_ranges():
            if _eq(value, x):
                return start
        raise ValueError(f"{x} is not in list")

    @abstractmethod
    def iter_ranges(self) -> Iterator[Tuple[int, int, T]]:
        """
        Fast but *not* update-safe iterator of the ranges.

        :return: yields each range one by one
        """
        raise NotImplementedError

    def iter_ranges_by_id(self, the_id: int) -> Iterator[Tuple[int, int, T]]:
        """
        Iterator of the range for this ID.

        .. note::
            The start and stop of the range will be reduced to just the ID

        This method purpose is so one a control method can select which
        iterator to use.

        :return: yields the one range
        """

        the_id = self._check_id_in_range(the_id)
        for (_, stop, value) in self.iter_ranges():
            if the_id < stop:
                yield (the_id, the_id + 1, value)
                break

    @abstractmethod
    def iter_ranges_by_slice(
            self, slice_start: int, slice_stop: int) -> Iterator[
                Tuple[int, int, T]]:
        """
        Fast but *not* update-safe iterator of the ranges covered by this
        slice.

        .. note::
            The start and stop of the range will be reduced to just the
            IDs inside the slice.

        :return: yields each range one by one
        """
        raise NotImplementedError

    def iter_ranges_by_ids(self, ids: IdsType) -> Iterator[
            Tuple[int, int, T]]:
        """
        Fast but *not* update-safe iterator of the ranges covered by these IDs.

        For consecutive IDs where the elements have the same value a single
        range may be yielded.

        .. note::
            The start and stop of the range will be reduced to just the IDs

        :return: yields each range one by one
        :rtype: iterable
        """
        range_pointer = 0
        result = None
        ranges = list(self.iter_ranges())
        for _id_value in ids:
            id_value = int(_id_value)

            # check if ranges reset so too far ahead
            if id_value < ranges[range_pointer][0]:
                range_pointer = 0
                while id_value > ranges[range_pointer][0]:
                    range_pointer += 1

            # check if pointer needs to move on
            while id_value >= ranges[range_pointer][1]:
                range_pointer += 1
            if result is not None:
                if (result[1] == id_value and _eq(
                        result[2], ranges[range_pointer][2])):
                    result = (result[0], id_value + 1, result[2])
                    continue
                yield result
            result = (id_value, id_value + 1, ranges[range_pointer][2])
        if result is not None:
            yield result

    @abstractmethod
    def get_default(self) -> Optional[T]:
        """
        Gets the default value of the list.
        Just in case we later allow to increase the number of elements.

        :return: Default value
        """
        raise NotImplementedError

    def __add__(self, other: Union[float, AbstractList[float]]
                ) -> AbstractList[float]:
        """
        Support for ``new_list = list1 + list2``.
        Applies the add operator over this and other to create a new list.
        The values of the new list are created on the fly so any changes to
        the original lists are reflected.

        :param other: another list
        :type other: AbstractList
        :return: new list
        :rtype: AbstractList
        :raises TypeError:
        """
        if isinstance(other, AbstractList):
            d_operation: Callable[[Any, float], float] = lambda x, y: x + y
            return DualList(
                left=self, right=other, operation=d_operation)
        if is_number(other):
            s_operation: Callable[[Any], float] = lambda x: x + other
            return SingleList(a_list=self, operation=s_operation)
        raise TypeError("__add__ operation only supported for other "
                        "RangedLists and numerical Values")

    def __sub__(self, other: Union[float, AbstractList[float]]
                ) -> AbstractList[float]:
        """
        Support for ``new_list = list1 - list2``.
        Applies the subtract operator over this and other to create a new list.
        The values of the new list are created on the fly so any changes to
        the original lists are reflected.

        :param other: another list
        :type other: AbstractList
        :return: new list
        :rtype: AbstractList
        :raises TypeError:
        """
        if isinstance(other, AbstractList):
            d_operation: Callable[[Any, float], float] = lambda x, y: x - y
            return DualList(
                left=self, right=other, operation=d_operation)
        if is_number(other):
            s_operation: Callable[[Any], float] = lambda x: x - other
            return SingleList(a_list=self, operation=s_operation)
        raise TypeError("__sub__ operation only supported for other "
                        "RangedLists and numerical Values")

    def __mul__(self, other: Union[float, AbstractList[float]]
                ) -> AbstractList[float]:
        """
        Support for ``new_list = list1 * list2``.
        Applies the multiply operator over this and other.
        The values of the new list are created on the fly so any changes to
        the original lists are reflected.

        :param other: another list
        :type other: AbstractList
        :return: new list
        :rtype: AbstractList
        :raises TypeError:
        """
        if isinstance(other, AbstractList):
            d_operation: Callable[[Any, float], float] = lambda x, y: x * y
            return DualList(
                left=self, right=other, operation=d_operation)
        if is_number(other):
            s_operation: Callable[[Any], float] = lambda x: x * other
            return SingleList(a_list=self, operation=s_operation)
        raise TypeError("__mul__ operation only supported for other "
                        "RangedLists and numerical Values")

    def __truediv__(self, other: Union[float, AbstractList[float]]
                    ) -> AbstractList[float]:
        """
        Support for ``new_list = list1 / list2``.
        Applies the division operator over this and other to create a
        new list.
        The values of the new list are created on the fly so any changes to
        the original lists are reflected.

        :param other: another list
        :type other: AbstractList
        :return: new list
        :rtype: AbstractList
        :raises TypeError:
        """
        if isinstance(other, AbstractList):
            d_operation: Callable[[Any, float], float] = lambda x, y: x / y
            return DualList(
                left=self, right=other, operation=d_operation)
        if is_number(other):
            if _is_zero(other):
                raise ZeroDivisionError()
            s_operation: Callable[[Any], float] = lambda x: x / other
            return SingleList(a_list=self, operation=s_operation)
        raise TypeError("__truediv__ operation only supported for other "
                        "RangedLists and numerical Values")

    def __floordiv__(self, other: Union[float, AbstractList[float]]
                     ) -> AbstractList[int]:
        """
        Support for ``new_list = list1 // list2``.
        Applies the floor division operator over this and other.

        :param other: another list
        :type other: AbstractList
        :return: new list
        :rtype: AbstractList
        :raises TypeError:
        """
        if isinstance(other, AbstractList):
            d_operation: Callable[[Any, float], int] = lambda x, y: int(x // y)
            return DualList(
                left=self, right=other, operation=d_operation)
        if is_number(other):
            if _is_zero(other):
                raise ZeroDivisionError()
            s_operation: Callable[[Any], int] = lambda x: int(x / other)
            return SingleList(a_list=self, operation=s_operation)
        raise TypeError("__floordiv__ operation only supported for other "
                        "RangedLists and numerical Values")

    def apply_operation(
            self, operation: Callable[[T], U]) -> AbstractList[U]:
        """
        Applies a function on the list to create a new one.
        The values of the new list are created on the fly so any changes
        to the original lists are reflected.

        :param operation:
            A function that can be applied over the individual values to
            create new ones.
        :return: new list
        :rtype: AbstractList
        """
        return SingleList(a_list=self, operation=operation)


class SingleList(AbstractList[ResultType], Generic[T, ResultType],
                 metaclass=AbstractBase):
    """
    A List that performs an operation on the elements of another list.
    """
    __slots__ = [
        "_a_list", "_operation"]

    def __init__(self, a_list: AbstractList[T],
                 operation: Callable[[T], ResultType],
                 key: Optional[str] = None):
        """
        :param AbstractList a_list: The list to perform the operation on
        :param callable operation:
            A function which takes a single value and returns the result of
            the operation on that value
        :param key: The dict key this list covers.
            This is used only for better Exception messages
        """
        super().__init__(size=len(a_list), key=key)
        self._a_list = a_list
        self._operation = operation

    @overrides(AbstractList.range_based)
    def range_based(self) -> bool:
        return self._a_list.range_based()

    @overrides(AbstractList.get_value_by_id)
    def get_value_by_id(self, the_id: int) -> ResultType:
        return self._operation(self._a_list.get_value_by_id(the_id))

    @overrides(AbstractList.get_single_value_by_slice)
    def get_single_value_by_slice(
            self, slice_start: int, slice_stop: int) -> ResultType:
        return self._operation(self._a_list.get_single_value_by_slice(
            slice_start, slice_stop))

    @overrides(AbstractList.get_single_value_by_ids)
    def get_single_value_by_ids(self, ids: IdsType) -> ResultType:
        return self._operation(self._a_list.get_single_value_by_ids(ids))

    @overrides(AbstractList.iter_ranges)
    def iter_ranges(self) -> Iterator[Tuple[int, int, ResultType]]:
        for (start, stop, value) in self._a_list.iter_ranges():
            yield (start, stop, self._operation(value))

    @overrides(AbstractList.get_default)
    def get_default(self) -> Optional[ResultType]:
        default = self._a_list.get_default()
        if default is None:
            return None
        return self._operation(default)

    @overrides(AbstractList.iter_ranges_by_slice)
    def iter_ranges_by_slice(
            self, slice_start: int, slice_stop: int
            ) -> Iterator[Tuple[int, int, ResultType]]:
        for (start, stop, value) in \
                self._a_list.iter_ranges_by_slice(slice_start, slice_stop):
            yield (start, stop, self._operation(value))


class DualList(AbstractList[ResultType], Generic[T, U, ResultType],
               metaclass=AbstractBase):
    """
    A list which combines two other lists with an operation.
    """
    __slots__ = [
        "_left", "_operation", "_right"]

    def __init__(self, left: AbstractList[T], right: AbstractList[U],
                 operation: Callable[[T, U], ResultType],
                 key: Optional[str] = None):
        """
        :param AbstractList left: The first list to combine
        :param AbstractList right: The second list to combine
        :param callable operation:
            The operation to perform as a function that takes two values and
            returns the result of the operation
        :param key:
            The dict key this list covers.
            This is used only for better Exception messages
        :raises ValueError: If list are not the same size
        """
        if len(left) != len(right):
            raise ValueError("Two list must have the same size")
        super().__init__(size=len(left), key=key)
        self._left = left
        self._right = right
        self._operation = operation

    @overrides(AbstractList.range_based)
    def range_based(self) -> bool:
        return self._left.range_based() and self._right.range_based()

    @overrides(AbstractList.get_value_by_id)
    def get_value_by_id(self, the_id: int) -> ResultType:
        return self._operation(
            self._left.get_value_by_id(the_id),
            self._right.get_value_by_id(the_id))

    @overrides(AbstractList.get_single_value_by_slice)
    def get_single_value_by_slice(
            self, slice_start: int, slice_stop: int) -> ResultType:
        return self._operation(
            self._left.get_single_value_by_slice(slice_start, slice_stop),
            self._right.get_single_value_by_slice(slice_start, slice_stop))

    @overrides(AbstractList.get_single_value_by_ids)
    def get_single_value_by_ids(self, ids: IdsType) -> ResultType:
        return self._operation(
            self._left.get_single_value_by_ids(ids),
            self._right.get_single_value_by_ids(ids))

    @overrides(AbstractList.iter_by_slice)
    def iter_by_slice(
            self, slice_start: int, slice_stop: int) -> Iterator[ResultType]:
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
                right_values = self._right.iter_by_slice(
                    slice_start, slice_stop)
                for (start, stop, left_value) in left_iter:
                    for _ in range(start, stop):
                        yield self._operation(left_value, next(right_values))
        else:
            if self._right.range_based():

                # Right list is range based left is not
                left_values = self._left.iter_by_slice(
                    slice_start, slice_stop)
                right_iter = self._right.iter_ranges_by_slice(
                    slice_start, slice_stop)
                for (start, stop, right_value) in right_iter:
                    for _ in range(start, stop):
                        yield self._operation(next(left_values), right_value)
            else:

                # Neither list is range based
                left_values = self._left.iter_by_slice(slice_start, slice_stop)
                right_values = self._right.iter_by_slice(
                    slice_start, slice_stop)
                while True:
                    try:
                        yield self._operation(
                            next(left_values), next(right_values))
                    except StopIteration:
                        return

    @overrides(AbstractList.iter_ranges)
    def iter_ranges(self) -> Iterator[Tuple[int, int, ResultType]]:
        left_iter = self._left.iter_ranges()
        right_iter = self._right.iter_ranges()
        return self._merge_ranges(left_iter, right_iter)

    @overrides(AbstractList.iter_ranges_by_slice)
    def iter_ranges_by_slice(
            self, slice_start: int, slice_stop: int) -> Iterator[
                Tuple[int, int, ResultType]]:
        left_iter = self._left.iter_ranges_by_slice(slice_start, slice_stop)
        right_iter = self._right.iter_ranges_by_slice(slice_start, slice_stop)
        return self._merge_ranges(left_iter, right_iter)

    def _merge_ranges(self, left_iter: Iterator[Tuple[int, int, T]],
                      right_iter: Iterator[Tuple[int, int, U]]
                      ) -> Iterator[Tuple[int, int, ResultType]]:
        (left_start, left_stop, left_value) = next(left_iter)
        (right_start, right_stop, right_value) = next(right_iter)
        try:
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
        except StopIteration:
            return

    @overrides(AbstractList.get_default)
    def get_default(self) -> Optional[ResultType]:
        l_default = self._left.get_default()
        if l_default is None:
            return None
        r_default = self._right.get_default()
        if r_default is None:
            return None
        return self._operation(l_default, r_default)
