from spinn_utilities.ranged.abstract_list import AbstractList
from spinn_utilities.abstract_base import AbstractBase

from six import add_metaclass


@add_metaclass(AbstractBase)
class DualList(AbstractList):
    """ A list which combines two other lists with an operation.
    """

    def __init__(self, left, right, operation, key=None):
        """

        :param left: The first list to combine
        :param right: The second list to combine
        :param operation:\
            The operation to perform as a function that takes two values and\
            returns the result of the operation
        :param key:\
            The dict key this list covers.
            This is used only for better Exception messages
        """
        if left._size != right._size:
            raise Exception("Two list must have the same size")
        AbstractList.__init__(self, size=left._size, key=key)
        self._left = left
        self._right = right
        self._operation = operation

    def range_based(self):
        return self._left.range_based() and self._right.range_based()

    def get_value_by_id(self, id):  # @ReservedAssignment
        return self._operation(
            self._left.get_value_by_id(id), self._right.get_value_by_id(id))

    def get_value_by_slice(self, slice_start, slice_stop):
        return self._operation(
            self._left.get_value_by_slice(slice_start, slice_stop),
            self._right.get_value_by_slice(slice_start, slice_stop))

    def get_value_by_ids(self, ids):
        return self._operation(
            self._left.get_value_by_ids(ids),
            self._right.get_value_by_ids(ids))

    def iter_by_slice(self, slice_start, slice_stop):
        """
        Fast NOT update safe iterator of all elements in the slice

        Note: Duplicate/Repeated elements are yielded for each id

        :return: yields each element one by one
        """
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
                right_iter = self._right.iter_by_slice(slice_start, slice_stop)
                for (start, stop, left_value) in left_iter:
                    for _ in range(start, stop):
                        yield self._operation(left_value, right_iter.next())
        else:
            if self._right.range_based():

                # Right list is range based left is not
                left_iter = self._left.iter_by_slice(
                    slice_start, slice_stop)
                right_iter = self._right.iter_ranges_by_slice(
                    slice_start, slice_stop)
                for (start, stop, right_value) in right_iter:
                    for _ in range(start, stop):
                        yield self._operation(left_iter.next(), right_value)
            else:

                # Neither list is range based
                left_iter = self._left.iter_by_slice(slice_start, slice_stop)
                right_iter = self._right.iter_by_slice(slice_start, slice_stop)
                while True:
                    yield self._operation(left_iter.next(), right_iter.next())

    def iter_ranges(self):
        left_iter = self._left.iter_ranges()
        right_iter = self._right.iter_ranges()
        return self._merge_ranges(left_iter, right_iter)

    def iter_ranges_by_slice(self, slice_start, slice_stop):
        left_iter = self._left.iter_ranges_by_slice(slice_start, slice_stop)
        right_iter = self._right.iter_ranges_by_slice(slice_start, slice_stop)
        return self._merge_ranges(left_iter, right_iter)

    def _merge_ranges(self, left_iter, right_iter):
        (left_start, left_stop, left_value) = left_iter.next()
        (right_start, right_stop, right_value) = right_iter.next()
        while True:
            yield (max(left_start, right_start),
                   min(left_stop, right_stop),
                   self._operation(left_value, right_value))
            if left_stop < right_stop:
                (left_start, left_stop, left_value) = left_iter.next()
            elif left_stop > right_stop:
                (right_start, right_stop, right_value) = right_iter.next()
            else:
                (left_start, left_stop, left_value) = left_iter.next()
                (right_start, right_stop, right_value) = right_iter.next()

    def get_default(self):
        self._operation(self._left.get_default(), self._right.get_default())
