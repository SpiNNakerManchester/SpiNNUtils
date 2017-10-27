from spinn_utilities.ranged.abstract_list import AbstractList
from spinn_utilities.abstract_base import AbstractBase, abstractmethod

from six import add_metaclass


@add_metaclass(AbstractBase)
class DualList(AbstractList):

    def __init__(self, left, right, operation, key=None):
        """
        Constructor for a ranged list.

        :param key: The dict key this list covers.
        This is used only for better Exception messages
        """
        if left._size != right._size:
            raise Exception("Two list must have the same size")
        AbstractList.__init__(self, size=left._size, key=key)
        self._left = left
        self._right = right
        self._operation = operation

    def get_value_by_id(self, id):
        return self._operation(
            self._left.get_value_by_id(id), self._right.get_value_by_id(id))

    def get_value_by_slice(self, slice_start, slice_stop):
        return self._operation(
            self._left.get_value_by_slice(slice_start, slice_stop),
            self._right.get_value_by_slice(slice_start, slice_stop))

    def get_value_by_ids(self, ids):
        return self._operation(
            self._left.get_value_by_ids(ids), self._right.get_value_by_ids(ids))

    def iter_by_slice(self, slice_start, slice_stop):
        """
        Fast NOT update safe iterator of all elements in the slice

        Note: Duplicate/Repeated elements are yielded for each id

        :return: yields each element one by one
        """
        ranges = self.iter_ranges_by_slice(slice_start, slice_stop)
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
        left_iter = self._left.iter_ranges()
        right_iter = self._right.iter_ranges()
        return self._merge_ranges(left_iter, right_iter)

    def iter_ranges_by_slice(self, slice_start, slice_stop):
        left_iter = self._left.iter_ranges_by_slice(slice_start, slice_stop)
        right_iter = self._right.iter_ranges_by_slice(slice_start, slice_stop)
        return self._merge_ranges(left_iter, right_iter)

    def _merge_ranges(self, left_iter, right_iter):
        left = left_iter.next()
        right = right_iter.next()
        while True:
            yield (max(left[0], right[0]),
                   min(left[1], right[1]),
                   self._operation(left[2], right[2]))
            if left[1] < right[1]:
                left = left_iter.next()
            elif left[1] > right[1]:
                right = right_iter.next()
            else:
                left = left_iter.next()
                right = right_iter.next()

    def get_default(self):
        self._operation(self._left.get_default(), self._right.get_default())
