import sys


class AbstractSized(object):
    """
    Based class for slice and id checking against size
    """

    __slots__ = ("_size")

    def __init__(self, size):
        """
        Constructor for a ranged list.

        :param size: Fixed length of the list
        """
        self._size = int(round(size))

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
            raise TypeError("Invalid argument type {}.".format(type(id)))
        if id >= self._size:
            if isinstance(id, (int, long)):
                raise IndexError(
                    "The index {0!d} is out of range.".format(id))
            raise TypeError("Invalid argument type {}.".format(type(id)))

    def _check_slice_in_range(self, slice_start, slice_stop):
        if slice_start is None:
            slice_start = 0
        elif slice_start < 0:
            slice_start = self._size + slice_start
            if slice_start < 0:
                if isinstance(slice_start, (int, long)):
                    raise IndexError(
                        "The range_start {} is out of range."
                        "".format(slice_start))
                raise TypeError("Invalid argument type {}."
                                "".format(type(slice_start)))
        if slice_stop is None or slice_stop == sys.maxsize:
            slice_stop = self._size
        elif slice_stop < 0:
            slice_stop = self._size + slice_stop
        if slice_start > slice_stop:
            if not isinstance(slice_start, (int, long)):
                raise TypeError("Invalid argument type {}."
                                "".format(type(slice_start)))
            if not isinstance(slice_stop, (int, long)):
                raise TypeError("Invalid argument type {}."
                                "".format(type(slice_start)))
            raise IndexError(
                "The range_start {} is after the range stop {}."
                "".format(slice_start, slice_stop))
        if slice_stop > len(self):
            if isinstance(slice_stop, (int, long)):
                raise IndexError(
                    "The range_stop {} is out of range."
                    "".format(slice_stop))
            raise TypeError("Invalid argument type {}."
                            "".format(type(slice_stop)))
        return slice_start, slice_stop
