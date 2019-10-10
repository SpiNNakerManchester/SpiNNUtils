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
import itertools
import logging
import sys
import numpy
from six import integer_types

logger = logging.getLogger(__file__)


class AbstractSized(object):
    """ Base class for slice and ID checking against size.
    """

    __slots__ = [
        "_size"]

    def __init__(self, size):
        """
        :param size: Fixed length of the list
        """
        self._size = max(int(round(size)), 0)

    def __len__(self):
        """ Size of the list, irrespective of actual values.

        :return: the initial and Fixed size of the list
        """
        return self._size

    @staticmethod
    def _is_id_type(id):  # @ReservedAssignment
        """ Check if the given ID has a type acceptable for IDs. """
        return isinstance(id, integer_types)

    def _check_id_in_range(self, id):  # @ReservedAssignment
        if id < 0:
            if self._is_id_type(id):
                raise IndexError(
                    "The index {} is out of range.".format(id))
            # pragma: no cover
            raise TypeError("Invalid argument type {}.".format(type(id)))
        if id >= self._size:
            if self._is_id_type(id):
                raise IndexError(
                    "The index {0} is out of range.".format(id))
            raise TypeError("Invalid argument type {}.".format(type(id)))

    def _check_slice_in_range(self, slice_start, slice_stop):
        if slice_start is None:
            slice_start = 0
        elif slice_start < 0:
            slice_start = self._size + slice_start
            if slice_start < 0:
                if not self._is_id_type(slice_start):
                    raise TypeError("Invalid argument type {}.".format(
                        type(slice_start)))
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
                raise TypeError("Invalid argument type {}.".format(
                    type(slice_start)))
            if not self._is_id_type(slice_stop):
                raise TypeError("Invalid argument type {}.".format(
                    type(slice_start)))
            logger.warning(
                "Specified slice has a start %d greater than its stop %d "
                "(based on size %d). Therefore slice will be empty",
                slice_start, slice_stop, self._size)
            return (self._size, self._size)
        if slice_stop > len(self):
            if not self._is_id_type(slice_stop):
                raise TypeError("Invalid argument type {}.".format(
                    type(slice_start)))
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
        """ Gets the list of IDs covered by this selector. \
            The types of selector currently supported are:

        None:
            Returns all IDs.

        slice: Standard python slice.
            Negative values and values larger than size are handled using\
            slices's indices method. \
            This could result in am empty list.

        int: (or long) Handles negative values as normal.
            Checks if ID is within expected range.

        iterator of bools: Used as a mask.
            If the length of the mask is longer or shorted than number of IDs \
            the result is the shorter of the two, \
            with the remainder of the longer ignored.

        iterator of int (long) but not bool:
            Every value checked that it is with the range 0 to size. \
            Negative values are *not* allowed. \
            Original order and duplication is respected so result may be\
            unordered and contain duplicates.

        :param selector: Some object that identifies a range of IDs.
        :param warn: \
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
            elif all(isinstance(item, (integer_types, numpy.integer))
                     for item in selector):
                # list converts any specific numpy types
                ids = list(selector)
                for _id in ids:
                    if _id < 0:
                        raise TypeError(
                            "Selector includes the ID {} which is less than "
                            "zero".format(_id))
                    if _id >= self._size:
                        raise TypeError(
                            "Selector includes the ID {} which not less than "
                            "the size {}".format(_id, self._size))
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

        if isinstance(selector, integer_types):
            if selector < 0:
                selector = self._size + selector
            if selector < 0 or selector >= self._size:
                raise TypeError("Selector {} is unsupproted for size {} "
                                "".format(selector-self._size, self._size))
            return [selector]

        raise TypeError("Unexpected selector type {}".format(type(selector)))
