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
from typing import (
    Dict, FrozenSet, Iterable, Iterator, MutableSequence, Optional, Sequence,
    Set, Tuple, Union,
    Generic, TypeVar, overload)
from typing_extensions import TypeAlias
from spinn_utilities.abstract_base import AbstractBase, abstractmethod
#: :meta private:
T = TypeVar("T")
# Can't be Iterable[str] or Sequence[str] because that includes str itself
_StrSeq: TypeAlias = Union[
    MutableSequence[str], Tuple[str, ...], FrozenSet[str], Set[str]]
_Keys: TypeAlias = Optional[Union[str, _StrSeq]]


class AbstractDict(Generic[T], metaclass=AbstractBase):
    """
    Base class for the :py:class:`RangeDictionary` and *all* views.
    This allows the users to not have to worry if they have a view.
    """
    __slots__ = ()

    @overload
    def get_value(self, key: str) -> T:
        ...

    @overload
    def get_value(self, key: Optional[_StrSeq]) -> Dict[str, T]:
        ...

    @abstractmethod
    def get_value(self, key: _Keys) -> Union[T, Dict[str, T]]:
        """
        Gets a single shared value for all IDs covered by this view.

        :param key: The key or keys to get the value of. Use `None` for all
        :type key: str or iterable(str) or None
        :return: If key is a str, this returns the single object.
            If key is iterable (list, tuple, set, etc.) of str (or `None`),
            returns a dictionary object
        :raises ~spinn_utilities.ranged.MultipleValuesException:
            If even one of the keys has multiple values set.
            But not if other keys not asked for have multiple values
        """
        raise NotImplementedError

    @abstractmethod
    def keys(self) -> Iterable[str]:
        """
        Returns the keys in the dictionary

        :return: keys in the dict
        """
        raise NotImplementedError

    @abstractmethod
    def set_value(
            self, key: str, value: T, use_list_as_value: bool = False):
        """
        Sets a already existing key to the new value.
        All IDs in the whole range or view will have this key set.

        .. warning::
            This method does not allow adding keys.
            Using `dict[str] =` will add a new key, but it is not supported
            for views.

        .. warning::
            If a View is created over multiple ranges this method would
            raise a `KeyError` if any the ranges does not have the key.
            (Currently multiple ranges not yet supported.)

        :param key: key to value being set
        :type key: str
        :param value: any object
        :param use_list_as_value: True if the value *is* a list
        :raise KeyError: If a new key is being used.
        """
        raise NotImplementedError

    @abstractmethod
    def ids(self) -> Sequence[int]:
        """
        Returns the IDs in range or view.
        If the view is setup with IDs out of numerical order the order used
        to create the view is maintained.

        .. note::
            If indexing into a view, you are picking the X'th ID.
            So if the IDs are `[2,3,4,5]` the `view[2]` will be the data for
            ID `4` and not `2`

        :return: list of IDs
        :rtype: list(int)
        """
        raise NotImplementedError

    @overload
    def iter_all_values(self, key: str, update_safe=False) -> Iterator[T]:
        ...

    @overload
    def iter_all_values(self, key: Optional[_StrSeq],
                        update_safe: bool = False) -> Iterator[Dict[str, T]]:
        ...

    @abstractmethod
    def iter_all_values(self, key: _Keys, update_safe: bool = False):
        """
        Iterates over the value(s) for all IDs covered by this view.
        There will be one yield for each ID even if values are repeated.

        :param key:
            The key or keys to get the value of. Use `None` for all keys
        :type key: str or iterable(str) or None
        :param update_safe: If set True the iteration will work even if values
            are updated during iteration. If left False the iterator may be
            faster but behaviour is *undefined* and *unchecked* if *any*
            values are changed during iteration.
        :return: If key is a str, this yields single objects.
            If key is iterable (list, tuple, set, etc.) of str (or `None`),
            yields dictionary objects
        """
        raise NotImplementedError

    @overload
    def get_ranges(self, key: None = None) -> Sequence[Tuple[
            int, int, Dict[str, T]]]:
        ...

    @overload
    def get_ranges(self, key: str) -> Sequence[Tuple[int, int, T]]:
        ...

    @overload
    def get_ranges(self, key: _StrSeq) -> Sequence[Tuple[
            int, int, Dict[str, T]]]:
        ...

    def get_ranges(self, key: _Keys = None) -> Sequence[Tuple[
            int, int, Union[T, Dict[str, T]]]]:
        """
        Lists the ranges(s) for all IDs covered by this view.
        There will be one yield for each range which may cover one or
        more IDs.

        .. note::
            As the data is created in a single call this is not affected
            by any updates.

        :param key: The key or keys to get the value of. Use `None` for all
        :type key: str or iterable(str) or None
        :return: List of tuples of (`start`, `stop`, `value`).
            `start` is *inclusive* so is the first ID in the range.
            `stop` is *exclusive* so is the last ID in the range + 1.
            If `key` is a str, `value` is a single object.
            If `key` is iterable (list, tuple, set, etc.) of str (or `None`)
            `value` is a dictionary object
        """
        return list(self.iter_ranges(key=key))

    @overload
    def iter_ranges(self, key: str) -> Iterator[Tuple[int, int, T]]:
        ...

    @overload
    def iter_ranges(self, key: Optional[_StrSeq]) -> Iterator[Tuple[
            int, int, Dict[str, T]]]:
        ...

    @abstractmethod
    def iter_ranges(self, key: _Keys = None
                    ) -> Union[Iterator[Tuple[int, int, T]],
                               Iterator[Tuple[int, int, Dict[str, T]]]]:
        """
        Iterates over the ranges(s) for all IDs covered by this view.
        There will be one yield for each range which may cover one or
        more IDs.

        .. warning::
            This iterator is *not* update safe!
            Behaviour is *undefined* and *unchecked* if *any* values are
            changed during iteration.

        :param key: The key or keys to get the value of. Use `None` for all
        :type key: str or iterable(str) or None
        :return: yields tuples of (`start`, `stop`, `value`).
            `start` is *inclusive* so is the first ID in the range.
            `stop` is *exclusive* so is the last ID in the range + 1.
            If `key` is a str, `value` is a single object.
            If `key` is iterable (list, tuple, set, etc.) of str (or `None`),
            `value` is a dictionary object
        """
        raise NotImplementedError

    @abstractmethod
    def get_default(self, key: str) -> Optional[T]:
        """
        Gets the default value for a single key.
        Unless changed, the default is the original value.

        .. note::
            Does not change any values but only changes what ``reset_value``
            would do

        :param key: Existing dict key
        :type key: str
        :return: default for this key.
        """
        raise NotImplementedError

    def items(self) -> Sequence[Tuple[str, T]]:
        """
        Returns a list of (``key``, ``value``) tuples.
        Works only if the whole ranges/view has single values.

        If the ``key`` is a str, the ``value``\\s are single objects.
        If the ``key`` is iterable (list, tuple, set, etc.) of str (or `None`),
        the ``value``\\s are dictionary objects.

        :return: List of (``key``, ``value``) tuples
        :rtype: list(tuple)
        :raises ~spinn_utilities.ranged.MultipleValuesException:
            If even one of the keys has multiple values set.
        """
        results = []
        for key in self.keys():
            value = self.get_value(key)
            results.append((key, value))
        return results

    def iteritems(self) -> Iterator[Tuple[str, T]]:
        """
        Iterates over the (``key``, ``value``) tuples.
        Works only if the whole ranges/view has single values.

        If the ``key`` is a str, the ``value``\\s are single objects.
        If the ``key`` is iterable (list, tuple, set, etc.) of str (or `None`),
        the ``value``\\s are dictionary objects

        This function is safe for value updates but may miss new keys
        added during iteration.

        :return: yield (``key``, ``value``) tuples
        :rtype: iterable(tuple)
        :raises ~spinn_utilities.ranged.MultipleValuesException:
            If even one of the keys has multiple values set.
        """
        for key in self.keys():
            yield (key, self.get_value(key))

    def values(self) -> Sequence[T]:
        """
        Returns a list of values.
        Works only if the whole ranges/view has single values.

        If a key is a str, its value is a single object.
        If a key is an iterable (list, tuple, set, etc.) of str (or `None`),
        its value is a dictionary object.

        :return: List of values
        :raises ~spinn_utilities.ranged.MultipleValuesException:
            If even one of the keys has multiple values set.
        """
        results = []
        for key in self.keys():
            value = self.get_value(key)
            results.append(value)
        return results

    def itervalues(self) -> Iterator[T]:
        """
        Iterates over the values.
        Works only if the whole ranges/view has single values.

        If a key is a str, its value is a single object.
        If a key is an iterable (list, tuple, set, etc.) of str (or `None`),
        its value is a dictionary object.

        This function is safe for value updates but may miss new keys
        added during iteration.

        :return: yield values
        :raises ~spinn_utilities.ranged.MultipleValuesException:
            If even one of the keys has multiple values set.
        """
        for key in self.keys():
            yield self.get_value(key)

    def __contains__(self, key: Union[str, int]) -> bool:
        """
        Checks if the key is a dictionary key or a range ID.

        :param key: Dictionary key or ID to check
        :type key: str or int
        :return: True if the str key is one of the dict keys or
            if the int key is one of the range IDs. Otherwise False
        :rtype: bool
        """
        if isinstance(key, str):
            return key in self.keys()
        if isinstance(key, int):
            return key in self.ids()
        raise KeyError(f"Unexpected key type: {type(key)}")

    def has_key(self, key: str) -> bool:
        """
        As the Deprecated dict ``has_keys`` function.

        .. note::
            Int keys to IDs are not supported.

        :param key: the key
        :type key: str
        :return: If the key is in dict
        :rtype: bool
        """
        return key in self.keys()

    def reset(self, key: str):
        """
        Sets the value(s) for a single key back to the default value.

        :param key: Existing dict key
        :type key: str
        :param default: Value to be used by reset
        """
        default = self.get_default(key)
        if default is None:
            raise ValueError(f"key '{key}' is not resettable")
        self.set_value(key, default)
