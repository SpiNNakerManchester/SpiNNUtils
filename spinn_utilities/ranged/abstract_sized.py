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

import itertools
import logging
import sys
import numpy

logger = logging.getLogger(__file__)


class AbstractSized(object):
    """
    Base class for slice and ID checking against size.
    Subclasses of this support the `len()` built-in.
    """

    __slots__ = (
        "_size")

    def __init__(self, size):
        """
        :param int size: Fixed length of the list.
        """
        # Strictly doesn't need to be int, but really should be!
        self._size = max(int(round(size)), 0)

    def __len__(self):
        """
        Size of the list, irrespective of actual values.

        :return: the initial and Fixed size of the list
        """
        return self._size

    @staticmethod
    def _is_id_type(the_id):
        """
        Check if the given ID has a type acceptable for IDs.
        """
        return isinstance(the_id, int)

    def _check_id_in_range(self, the_id):
        if the_id < 0:
            if self._is_id_type(the_id):
                raise IndexError(f"The index {the_id} is out of range.")
            # pragma: no cover
            raise TypeError(f"Invalid argument type {type(the_id)}.")
        if the_id >= self._size:
            if self._is_id_type(the_id):
                raise IndexError(f"The index {the_id} is out of range.")
            raise TypeError(f"Invalid argument type {type(the_id)}.")

    def _check_slice_in_range(self, slice_start, slice_stop):
        if slice_start is None:
            slice_start = 0
        elif slice_start < 0:
            slice_start = self._size + slice_start
            if slice_start < 0:
                if not self._is_id_type(slice_start):
                    raise TypeError(
                        f"Invalid argument type {type(slice_start)}.")
                logger.warning(
                    "Specified slice start was %d while size is only %d. "
                    "Therefore slice will start at index 0",
                    slice_start - self._size, self._size)
                slice_start = 0
        elif slice_start >= len(self):
            logger.warning(
                "Specified slice start was %d while size is only %d. "
                "Therefore slice will be empty",
                slice_start - self._size, self._size)
            return (self._size, self._size)

        if slice_stop is None or slice_stop == sys.maxsize:
            slice_stop = self._size
        elif slice_stop < 0:
            slice_stop = self._size + slice_stop

        if slice_start > slice_stop:
            if not self._is_id_type(slice_start):
                raise TypeError(f"Invalid argument type {type(slice_start)}.")
            if not self._is_id_type(slice_stop):
                raise TypeError(f"Invalid argument type {type(slice_stop)}.")
            logger.warning(
                "Specified slice has a start %d greater than its stop %d "
                "(based on size %d). Therefore slice will be empty",
                slice_start, slice_stop, self._size)
            return (self._size, self._size)
        if slice_stop > len(self):
            if not self._is_id_type(slice_stop):
                raise TypeError(f"Invalid argument type {type(slice_stop)}.")
            logger.warning(
                "Specified slice has a start %d equal to its stop %d "
                "(based on size %d). Therefore slice will be empty",
                slice_start, slice_stop, self._size)
        if slice_stop < 0:
            logger.warning(
                "Specified slice stop was %d while size is only %d. "
                "Therefore slice will be empty",
                slice_stop - self._size, self._size)
            return (self._size, self._size)
        elif slice_start > slice_stop:
            logger.warning(
                "Specified slice has a start %d greater than its stop %d "
                "(based on size %d). Therefore slice will be empty",
                slice_start, slice_stop, self._size)
            return (self._size, self._size)
        elif slice_start == slice_stop:
            logger.warning(
                "Specified slice has a start %d equal to its stop %d "
                "(based on size %d). Therefore slice will be empty",
                slice_start, slice_stop, self._size)
        elif slice_stop > len(self):
            logger.warning(
                "Specified slice stop was %d while size is only %d. "
                "Therefore slice will be truncated",
                slice_stop, self._size)
            slice_stop = self._size
        return slice_start, slice_stop

    def _check_mask_size(self, selector):
        if len(selector) < self._size:
            logger.warning(
                "The boolean mask is too short. The expected length was %d "
                "but the length was only %d. All the missing entries will be "
                "treated as False!", self._size, len(selector))
        elif len(selector) > self._size:
            logger.warning(
                "The boolean mask is too long. The expected length was %d "
                "but the length was only %d. All the missing entries will be "
                "ignored!", self._size, len(selector))

    def selector_to_ids(self, selector, warn=False):
        """
        Gets the list of IDs covered by this selector.
        The types of selector currently supported are:

        `None`:
            Returns all IDs.

        :py:class:`slice`: Standard python slice.
            Negative values and values larger than size are handled using
            slice's `indices` method.
            This could result in am empty list.

        :py:class:`int`: Handles negative values as normal.
            Checks if ID is within expected range.

        iterator(:py:class:`bool`): Used as a mask.
            If the length of the mask is longer or shorted than number of IDs
            the result is the shorter of the two,
            with the remainder of the longer ignored.

        iterator(:py:class:`int`) but not bool:
            Every value checked that it is with the range 0 to size.
            Negative values are *not* allowed.
            Original order and duplication is respected so result may be
            unordered and contain duplicates.

        :param selector: Some object that identifies a range of IDs.
        :param bool warn:
            If True, this method will warn about problems with the selector.
        :return: a (possibly sorted) list of IDs
        """
        # Check selector is an iterable using pythonic try
        try:
            iterator = iter(selector)
        except TypeError:
            iterator = None

        if iterator is not None:
            # bool is superclass of int so if any are bools all must be
            if any(isinstance(item, (bool, numpy.bool_)) for item in selector):
                if all(isinstance(item, (bool, numpy.bool_))
                       for item in selector):
                    if warn:
                        self._check_mask_size(selector)
                    return list(itertools.compress(
                        range(self._size), selector))
                raise TypeError(
                    "An iterable type must be all ints or all bools")
            elif all(isinstance(item, (int, numpy.integer))
                     for item in selector):
                # list converts any specific numpy types
                ids = list(selector)
                for _id in ids:
                    if _id < 0:
                        raise TypeError(
                            f"Selector includes the ID {_id} which is "
                            "less than zero")
                    if _id >= self._size:
                        raise TypeError(
                            f"Selector includes the ID {_id} which not "
                            f"less than the size {self._size}")
                return ids
            else:
                raise TypeError(
                    "An iterable type must be all ints or all bools")

        # OK lets try for None, int and slice after all
        if selector is None:
            if warn:
                logger.warning("None selector taken as all IDs")
            return range(self._size)

        if isinstance(selector, slice):
            (slice_start, slice_stop, step) = selector.indices(self._size)
            return range(slice_start, slice_stop, step)

        if isinstance(selector, int):
            if selector < 0:
                selector = self._size + selector
            if selector < 0 or selector >= self._size:
                raise TypeError(
                    f"Selector {selector-self._size} is unsupported "
                    f"for size {self._size}")
            return [selector]

        raise TypeError(f"Unexpected selector type {type(selector)}")
