# pylint: disable=redefined-builtin
from spinn_utilities.ranged.abstract_list import AbstractList
from spinn_utilities.abstract_base import AbstractBase

from six import add_metaclass


@add_metaclass(AbstractBase)
class SingleList(AbstractList):
    """ A List that performs an operation on the elements of another list
    """

    def __init__(self, a_list, operation, key=None):
        """

        :param a_list: The list to perform the operation on
        :param operation:\
            A function which takes a single value and returns the result of\
            the operation on that value
        :param key: The dict key this list covers.\
            This is used only for better Exception messages
        """
        AbstractList.__init__(self, size=len(a_list), key=key)
        self._a_list = a_list
        self._operation = operation

    def range_based(self):
        return self._a_list.range_based()

    def get_value_by_id(self, id):  # @ReservedAssignment
        return self._operation(self._a_list.get_value_by_id(id))

    def get_value_by_slice(self, slice_start, slice_stop):
        return self._operation(self._a_list.get_value_by_slice(
            slice_start, slice_stop))

    def get_value_by_ids(self, ids):
        return self._operation(self._a_list.get_value_by_ids(ids))

    def iter_ranges(self):
        for (start, stop, value) in self._a_list.iter_ranges():
            yield (start, stop, self._operation(value))

    def get_default(self):
        self._operation(self._a_list.get_default())

    def iter_ranges_by_slice(self, slice_start, slice_stop):
        for (start, stop, value) in \
                self._a_list.iter_ranges_by_slice(slice_start, slice_stop):
            yield (start, stop, self._operation(value))
