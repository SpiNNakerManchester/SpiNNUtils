from spinn_utilities.ranged.abstract_list import AbstractList
from spinn_utilities.abstract_base import AbstractBase, abstractmethod

from six import add_metaclass


@add_metaclass(AbstractBase)
class DualList(AbstractList):

    def __init__(self, left, right, key=None):
        """
        Constructor for a ranged list.

        :param size: Fixed length of the list
        :param default: Default value to given to all elements in the list
        :param key: The dict key this list covers.
        This is used only for better Exception messages
        """
        if left._size != right._size:
            raise Exception("Two list must have the same size")
        AbstractList.__init__(self, size=left._size, key=key)
        self._left = left
        self._right = right

    def get_value_by_id(self, id):
        return self._merge_values(
            self.left.get_value_by_id(id), self.right.get_value_by_id(id))

    def get_value_by_slice(self, slice_start, slice_stop):
        return self._merge_values(
            self.left.get_value_by_slice(slice_start, slice_stop),
            self.right.get_value_by_slice(slice_start, slice_stop))

    def get_value_by_ids(self, ids):
        return self._merge_values(
            self.left.get_value_by_ids(ids), self.right.get_value_by_ids(ids))

    def iter_ranges(self):
        left_iter = self._left.iter_ranges()
        right_iter = self._right.iter_ranges()
        return self._merge_ranges(left_iter, right_iter)

    @abstractmethod
    def _merge_values(self, left, right):
        pass

    def _merge_ranges(self, left_iter, right_iter):
        left = left_iter.next()
        right = right_iter.next()
        while True:
            yield (max(left[0], right[0]),
                   min(left[1], right[1]),
                   self._merge_values(left[2], right[2]))
            if left[1] < right[1]:
                left = left_iter.next()
            elif left[1] > right[1]:
                right = right_iter.next()
            else:
                left = left_iter.next()
                right = right_iter.next()

