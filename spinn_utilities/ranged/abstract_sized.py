# pylint: disable=redefined-builtin
import logging
import sys

logger = logging.getLogger(__file__)


class AbstractSized(object):
    """
    Base class for slice and id checking against size.
    """

    __slots__ = ("_size", )

    def __init__(self, size):
        """
        Constructor for a ranged list.

        :param size: Fixed length of the list
        """
        self._size = max((int(round(size)), 0))

    def __len__(self):
        """
        Size of the list, irrespective of actual values

        :return: the initial and Fixed size of the list
        """
        return self._size

    def _check_id_in_range(self, id):  # @ReservedAssignment
        if id < 0:
            if isinstance(id, (int, long)):
                raise IndexError(
                    "The index {} is out of range.".format(id))
            # pragma: no cover
            raise TypeError("Invalid argument type {}.".format(type(id)))
        if id >= self._size:
            if isinstance(id, (int, long)):
                raise IndexError(
                    "The index {0} is out of range.".format(id))
            raise TypeError("Invalid argument type {}.".format(type(id)))

    def _check_slice_in_range(self, slice_start, slice_stop):
        if slice_start is None:
            slice_start = 0
        elif slice_start < 0:
            slice_start = self._size + slice_start
            if slice_start < 0:
                msg = "Specified slice start was {} while size is only {}. " \
                      "Therefore slice will start at index 0" \
                      "".format(slice_start - self._size, self._size)
                logger.warn(msg)
                slice_start = 0
        elif slice_start >= len(self):
            msg = "Specified slice start was {} while size is only {}. " \
                  "Therefore slice will be empty" \
                  "".format(slice_start - self._size, self._size)
            logger.warn(msg)
            return (0, 0)

        if slice_stop is None or slice_stop == sys.maxsize:
            slice_stop = self._size
        elif slice_stop < 0:
            slice_stop = self._size + slice_stop
            if slice_stop < 0:
                msg = "Specified slice stop was {} while size is only {}. " \
                      "Therefore slice will be empty" \
                      "".format(slice_stop-self._size, self._size)
                logger.warn(msg)
                return (0, 0)
        elif slice_start > slice_stop:
            msg = "Specified slice has a start {} greater than its stop {} " \
                  "(based on size {}). Therefore slice will be empty" \
                  "".format(slice_start, slice_stop, self._size)
            logger.warn(msg)
            return (0, 0)
        elif slice_start == slice_stop:
            msg = "Specified slice has a start {} equal to its stop {} " \
                  "(based on size {}). Therefore slice will be empty" \
                  "".format(slice_start, slice_stop, self._size)
            logger.warn(msg)
        elif slice_stop > len(self):
            msg = "Specified slice stop was {} while size is only {}. " \
                  "Therefore slice will be truncated" \
                  "".format(slice_stop, self._size)
            logger.warn(msg)
            slice_stop = self._size
        return slice_start, slice_stop
