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
    Dict, Generator, Iterable, Iterator, Optional, Sequence, Tuple, Union,
    Generic, overload, TYPE_CHECKING)
from typing_extensions import TypeAlias
from spinn_utilities.overrides import overrides
from .abstract_dict import AbstractDict, T, _StrSeq
from .abstract_sized import AbstractSized
from .abstract_list import IdsType
from .ids_view import _IdsView
from .ranged_list import RangedList
from .single_view import _SingleView
from .slice_view import _SliceView
if TYPE_CHECKING:
    from .abstract_view import AbstractView

_KeyType: TypeAlias = Union[int, slice, Iterable[int]]
_Keys: TypeAlias = Union[None, str, _StrSeq]

_Range: TypeAlias = Tuple[int, int, T]
_SimpleRangeIter: TypeAlias = Iterator[_Range]
_CompoundRangeIter: TypeAlias = Iterator[Tuple[int, int, Dict[str, T]]]


class RangeDictionary(AbstractSized, AbstractDict[T], Generic[T]):
    """
    Main holding class for a range of similar Dictionary object.
    Keys in the dictionary must be str object and can not be removed.
    New keys can be added using the ``dict[str] = value`` format.
    The size (length of the list) is fixed and set at initialisation time.
    """
    __slots__ = [
        "_value_lists"]

    def __init__(self, size: int, defaults: Optional[Dict[str, T]] = None):
        """
        The Object is set up initially where every ID in the range will share
        the same value for each key. All keys must be of type str. The
        default values can be anything, including `None`.

        .. warning::
            Using mutable default values can result in weird problems.

        :param int size: Fixed number of IDs / Length of lists
        :param defaults: Default dictionary where all keys must be str
        :type defaults: dict(str,object)
        """
        super().__init__(size)
        self._value_lists: Dict[str, RangedList[T]] = dict()
        if defaults is not None:
            for key, value in defaults.items():
                self._value_lists[key] = self.list_factory(
                    size=size, value=value, key=key)

    def list_factory(self, size: int, value: T, key: str) -> RangedList[T]:
        """
        Defines which class or subclass of :py:class:`RangedList` to use.

        Main purpose is for subclasses to use a subclass or `RangedList`.
        All parameters are pass through ones to the List constructor

        :param size: Fixed length of the list
        :param value: value to given to all elements in the list
        :param key: The dict key this list covers.
        :return: AbstractList in this case a RangedList
        """
        return RangedList(size, value, key)

    def view_factory(self, key: _KeyType) -> AbstractView:
        """
        Main function for creating views.
        This is the preferred way of creating new views as it checks
        parameters and returns the most efficient view.

        .. note::
            The ``__getitem__`` methods called by `Object[id]` and similar
            defer to this method so are fine to use.

        The ID(s) used are the actual IDs in the range and not indexes on
        the list of IDs

        :param key: A single int ID, a Slice object, or an iterable of int IDs
        :return: A view over the range
        """
        # Key is an int - return single view
        if isinstance(key, int):
            key = self._check_id_in_range(key)
            return _SingleView(range_dict=self, the_id=key)

        # Key is a slice - return a sliced view
        if isinstance(key, slice):
            slice_start, slice_stop = self._check_slice_in_range(
                key.start, key.stop)

            if slice_start >= slice_stop:
                raise KeyError(f"{key} would result in an empty view")

            # Slice is really just one item - return a single view
            if slice_start == slice_stop - 1:
                return _SingleView(range_dict=self, the_id=slice_start)

            # Slice is continuous - return a slice view
            elif key.step is None or key.step == 1:
                return _SliceView(range_dict=self, start=slice_start,
                                  stop=slice_stop)

            # Slice is really a list of integers - change it and continue below
            key = range(self._size)[key]

        # Key can only now be an int iterable so make it a list and check
        key = list(key)
        if not all(isinstance(x, int) for x in key):
            raise KeyError("Only list/tuple of int are supported")

        # Key is really just a single int - return single view
        if len(key) == 1:
            return _SingleView(range_dict=self, the_id=key[0])

        # Key is really just a slice (i.e. one of each key in order without
        # holes) - return a slice view
        if len(key) == key[-1] - key[0] + 1:
            in_order = sorted(key)
            if in_order == key:
                return _SliceView(
                    range_dict=self, start=key[0], stop=key[-1] + 1)

        # Random jumble of int values - return an IDs view
        return _IdsView(range_dict=self, ids=key)

    @overload
    def __getitem__(self, key: str) -> RangedList[T]: ...

    @overload
    def __getitem__(self, key: _KeyType) -> AbstractView: ...

    def __getitem__(self, key: Union[str, _KeyType]
                    ) -> Union[RangedList[T], AbstractView]:
        """
        Support for the view[x] based the type of the key

        If key is a str, a list type object of :py:class:`AbstractList` is
        returned.
        Otherwise a view (:py:class:`AbstractView`) over part of the IDs in
        the dict is returned.

        Multiple str objects or `None` are not supported as keys here.

        :param key: a str, int, or iterable of int values
        :return: An AbstractList or AbstractView
        :rtype: AbstractList or AbstractView
        """
        if isinstance(key, str):
            return self._value_lists[key]
        return self.view_factory(key=key)

    @overload
    def get_value(self, key: str) -> T: ...

    @overload
    def get_value(self, key: Optional[_StrSeq] = None) -> Dict[str, T]: ...

    @overrides(AbstractDict.get_value, extend_defaults=True)
    def get_value(self, key: Union[str, None, _StrSeq] = None
                  ) -> Union[T, Dict[str, T]]:
        if isinstance(key, str):
            return self._value_lists[key].get_single_value_all()
        if key is None:
            key = list(self.keys())
        return {
            a_key: self._value_lists[a_key].get_single_value_all()
            for a_key in key}

    @overload
    def get_values_by_id(self, key: str, the_id: int) -> T: ...

    @overload
    def get_values_by_id(
            self, key: Optional[_StrSeq], the_id: int) -> Dict[str, T]: ...

    def get_values_by_id(
            self, key: Union[str, _StrSeq, None],
            the_id: int) -> Union[T, Dict[str, T]]:
        """
        Same as :py:meth:`get_value` but limited to a single ID.

        :param key: as :py:meth:`get_value`
        :param the_id: single int ID
        :return: See :py:meth:`get_value`
        """
        if isinstance(key, str):
            return self._value_lists[key].get_value_by_id(the_id)
        if key is None:
            key = list(self.keys())
        return {
            a_key: self._value_lists[a_key].get_value_by_id(the_id)
            for a_key in key}

    def get_list(self, key: str) -> RangedList[T]:
        """
        Gets the storage unit for a single key.

        .. note::
            Mainly intended by Views to access the data for one key directly.

        :param key: a key which must be present in the dict
        :type key: str
        :rtype: :py:class:`.ranged_list.RangedList`
        """
        return self._value_lists[key]

    @overload
    def update_safe_iter_all_values(
            self, key: str, ids: IdsType) -> Generator[T, None, None]: ...

    @overload
    def update_safe_iter_all_values(
            self, key: Optional[_StrSeq],
            ids: IdsType) -> Generator[Dict[str, T], None, None]: ...

    def update_safe_iter_all_values(
            self, key: Union[str, Optional[_StrSeq]],
            ids: IdsType) -> Generator[Union[T, Dict[str, T]], None, None]:
        """
        Same as
        :py:meth:`iter_all_values`
        but limited to a collection of IDs and update-safe.
        """
        return (
            self.get_values_by_id(key=key, the_id=id_value)
            for id_value in ids)

    @overload
    def iter_all_values(
            self, key: str, update_safe: bool = False) -> Iterator[T]:
        ...

    @overload
    def iter_all_values(self, key: Optional[_StrSeq],
                        update_safe: bool = False) -> Iterator[Dict[str, T]]:
        ...

    @overrides(AbstractDict.iter_all_values, extend_defaults=True)
    def iter_all_values(self, key: _Keys, update_safe: bool = False
                        ) -> Union[Iterator[T], Iterator[Dict[str, T]]]:
        if isinstance(key, str):
            if update_safe:
                return self._value_lists[key].iter()
            return iter(self._value_lists[key])
        else:  # Sub methods will check key type
            if update_safe:
                return self.update_safe_iter_all_values(
                    key, range(self._size))
            return iter(self._values_from_ranges(self.iter_ranges(key)))

    @overload
    def iter_values_by_slice(
            self, slice_start: int, slice_stop: int, key: str,
            update_safe: bool = False) -> Iterator[T]:
        ...

    @overload
    def iter_values_by_slice(
            self, slice_start: int, slice_stop: int,
            key: Optional[_StrSeq] = None,
            update_safe: bool = False) -> Iterator[Dict[str, T]]:
        ...

    def iter_values_by_slice(
            self, slice_start: int, slice_stop: int,
            key: Union[str, _StrSeq, None] = None,
            update_safe: bool = False) -> Union[
            Iterator[T], Iterator[Dict[str, T]]]:
        """
        Same as :py:meth:`iter_all_values` but limited to a simple slice.
        """
        if isinstance(key, str) and not update_safe:
            return self._value_lists[key].iter_by_slice(
                slice_start=slice_start, slice_stop=slice_stop)
        # Sub methods will check key type
        if update_safe:
            return self.update_safe_iter_all_values(
                key, range(slice_start, slice_stop))
        return self._values_from_ranges(self.iter_ranges_by_slice(
            slice_start=slice_start, slice_stop=slice_stop, key=key))

    @overload
    def iter_values_by_ids(
            self, ids: IdsType, key: str,
            update_safe: bool = False) -> Generator[T, None, None]:
        ...

    @overload
    def iter_values_by_ids(
            self, ids: IdsType, key: Optional[_StrSeq] = None,
            update_safe: bool = False) -> Generator[Dict[str, T], None, None]:
        ...

    def iter_values_by_ids(
            self, ids: IdsType, key: Union[str, _StrSeq, None] = None,
            update_safe: bool = False) -> Union[
            Generator[T, None, None], Generator[Dict[str, T], None, None]]:
        """
        Same as :py:meth:`iter_all_values` but limited to a simple slice.
        """
        if update_safe:
            return self.update_safe_iter_all_values(key, ids)
        return self._values_from_ranges(self.iter_ranges_by_ids(
            key=key, ids=ids))

    @staticmethod
    def _values_from_ranges(
            ranges: _SimpleRangeIter) -> Generator[T, None, None]:
        for (start, stop, value) in ranges:
            for _ in range(start, stop):
                yield value

    @overrides(AbstractDict.set_value)
    def set_value(
            self, key: str, value: T, use_list_as_value: bool = False) -> None:
        self._value_lists[key].set_value(
            value, use_list_as_value=use_list_as_value)

    def __setitem__(self, key: str, value: Union[T, RangedList[T]]) -> None:
        """
        Wrapper around set_value to support ``range["key"] =``

        .. note::
            ``range[int] =`` is not supported

        ``value`` can be a single object or ``None`` in
        which case every value in the list is set to that.
        ``value`` can be a collection but
        then it must be exactly the size of all lists in this dictionary.
        ``value`` can be an ``AbstractList``

        :param str key: Existing or *new* dictionary key
        :param value: List or value to create list based on.
        """
        if isinstance(key, str):
            if key in self:
                assert not isinstance(value, RangedList)
                self.set_value(key=key, value=value)
            elif isinstance(value, RangedList):
                assert self._size == len(value)
                self._value_lists[key] = value
                # TODO Make work for other kinds of AbstractList
            else:
                new_list = self.list_factory(
                    size=self._size, value=value, key=key)
                self._value_lists[key] = new_list
        elif isinstance(key, (slice, int, tuple, list)):
            raise KeyError("Setting of a slice/ids not supported")
        else:
            raise KeyError(f"Unexpected key type: {type(key)}")

    @overrides(AbstractDict.ids)
    def ids(self) -> Sequence[int]:
        """
        Returns a list of the IDs in this Range

        :return: a list of the IDs in this Range
        :rtype: list(int)
        """
        return list(range(self._size))

    @overrides(AbstractDict.has_key)
    def has_key(self, key: str) -> bool:
        return key in self._value_lists

    @overrides(AbstractDict.keys)
    def keys(self) -> Iterable[str]:
        return self._value_lists.keys()

    def _merge_ranges(
            self, range_iters: Dict[str, Iterator[Tuple[int, int, T]]]
            ) -> Iterator[Tuple[int, int, Dict[str, T]]]:
        current: Dict[str, T] = dict()
        ranges: Dict[str, Tuple[int, int, T]] = dict()
        start = 0
        stop = self._size
        keys = range_iters.keys()
        for key in keys:
            ranges[key] = next(range_iters[key])
            start = ranges[key][0]
            current[key] = ranges[key][2]
            stop = min(ranges[key][1], stop)
        yield (start, stop, current)
        while stop < self._size:
            current = dict()
            start = self._size
            next_stop = self._size
            for key in keys:
                try:
                    if ranges[key][1] == stop:
                        ranges[key] = next(range_iters[key])
                except StopIteration:
                    return
                start = min(max(ranges[key][0], stop), start)
                next_stop = min(ranges[key][1], next_stop)
                current[key] = ranges[key][2]
            stop = next_stop
            yield (start, stop, current)

    @overload
    def iter_ranges(self, key: str) -> Iterator[Tuple[int, int, T]]:
        ...

    @overload
    def iter_ranges(self, key: Optional[_StrSeq]) -> Iterator[Tuple[
            int, int, Dict[str, T]]]:
        ...

    @overrides(AbstractDict.iter_ranges)
    def iter_ranges(self, key: _Keys = None) -> Union[
            Iterator[Tuple[int, int, T]],
            Iterator[Tuple[int, int, Dict[str, T]]]]:
        if isinstance(key, str):
            return self._value_lists[key].iter_ranges()
        if key is None:
            keys = self.keys()
        else:
            keys = key
        return self._merge_ranges({
            a_key: self._value_lists[a_key].iter_ranges()
            for a_key in keys})

    @overload
    def iter_ranges_by_id(
            self, *, the_id: int, key: str) -> _SimpleRangeIter:
        ...

    @overload
    def iter_ranges_by_id(self, *, the_id: int,
                          key: Optional[_StrSeq] = None) -> _CompoundRangeIter:
        ...

    def iter_ranges_by_id(
            self, *, the_id: int,
            key: Union[str, _StrSeq, None] = None) -> Union[
            _SimpleRangeIter, _CompoundRangeIter]:
        """
        Same as :py:meth:`iter_ranges` but limited to one ID.

        :param key: see :py:meth:`iter_ranges` parameter key
        :param the_id:
            single ID which is the actual ID and not an index into IDs
        """
        if isinstance(key, str):
            return self._value_lists[key].iter_ranges_by_id(the_id=the_id)
        if key is None:
            key = list(self.keys())
        return self._merge_ranges({
            a_key: self._value_lists[a_key].iter_ranges_by_id(the_id=the_id)
            for a_key in key})

    @overload
    def iter_ranges_by_slice(
            self, key: str, slice_start: int,
            slice_stop: int) -> _SimpleRangeIter:
        ...

    @overload
    def iter_ranges_by_slice(
            self, key: Optional[_StrSeq], slice_start: int,
            slice_stop: int) -> _CompoundRangeIter:
        ...

    def iter_ranges_by_slice(
            self, key: Union[str, _StrSeq, None], slice_start: int,
            slice_stop: int) -> Union[_SimpleRangeIter, _CompoundRangeIter]:
        """
        Same as :py:meth:`iter_ranges` but limited to a simple slice.

        ``slice_start`` and ``slice_stop`` are actual ID values and not
        indexes into the IDs. They must also be actual values, so ``None``,
        ``max_int``, and negative numbers are not supported.

        :param key: see :py:meth:`iter_ranges` parameter ``key``
        :param slice_start: Inclusive i.e. first ID
        :param slice_stop:  Exclusive to last ID + 1
        :return: see :py:meth:`iter_ranges`
        """
        if isinstance(key, str):
            return self._value_lists[key].iter_ranges_by_slice(
                slice_start=slice_start, slice_stop=slice_stop)
        if key is None:
            key = list(self.keys())
        return self._merge_ranges({
            a_key: self._value_lists[a_key].iter_ranges_by_slice(
                slice_start=slice_start, slice_stop=slice_stop)
            for a_key in key})

    @overload
    def iter_ranges_by_ids(
            self, ids: IdsType, key: str) -> _SimpleRangeIter:
        ...

    @overload
    def iter_ranges_by_ids(
            self, ids: IdsType,
            key: Optional[_StrSeq] = None) -> _CompoundRangeIter:
        ...

    def iter_ranges_by_ids(
            self, ids: IdsType,
            key: Union[str, _StrSeq, None] = None) -> Union[
                _SimpleRangeIter, _CompoundRangeIter]:
        """
        Same as :py:meth:`iter_ranges` but limited to a collection of IDs.

        The IDs are actual ID values and not indexes into the IDs

        :param key: see :py:meth:`iter_ranges` parameter ``key``
        :param ids: Collection of IDs in the range
        :return: see :py:meth:`iter_ranges`
        """
        if isinstance(key, str):
            return self._value_lists[key].iter_ranges_by_ids(ids=ids)
        if key is None:
            key = list(self.keys())
        return self._merge_ranges({
            a_key: self._value_lists[a_key].iter_ranges_by_ids(ids=ids)
            for a_key in key})

    def set_default(self, key: str, default: T) -> None:
        """
        Sets the default value for a single key.

        .. note::
            Does not change any values but only changes what ``reset_value``
            would do

        .. warning::
            If called on a view, it sets the default for the *whole* range
            and not just the view.

        :param key: Existing dict key
        :type key: str
        :param default: Value to be used by reset; should not be mutable!
        """
        self._value_lists[key].set_default(default)

    @overrides(AbstractDict.get_default)
    def get_default(self, key: str) -> Optional[T]:
        return self._value_lists[key].get_default()

    def copy_into(self, other: RangeDictionary[T]) -> None:
        """
        Turns this dict into a copy of the other dict but keep its id.

        :param RangeDictionary other:
            Another ranged dictionary assumed created by cloning this one
        """
        for key in other.keys():
            value = other[key]
            if isinstance(value, RangedList):
                if key in self:
                    self._value_lists[key].copy_into(value)
                else:
                    self._value_lists[key] = value.copy()
            else:
                self._value_lists[key] = RangedList(
                    len(value), key=key)
                self._value_lists[key].copy_into(value)

    def copy(self) -> RangeDictionary[T]:
        """
        Make a copy of this dictionary. Inner ranged entities are deep copied,
        inner leaf values are shallow copied.

        :return: The copy.
        :rtype: RangeDictionary
        """
        copy: RangeDictionary[T] = RangeDictionary(self._size)
        copy.copy_into(self)
        return copy
