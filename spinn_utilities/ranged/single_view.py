# pylint: disable=redefined-builtin
from spinn_utilities.ranged.abstract_dict import AbstractDict
from spinn_utilities.ranged.abstract_view import AbstractView
from spinn_utilities.overrides import overrides


class _SingleView(AbstractView):
    __slots__ = [
        "_id"]

    def __init__(self, range_dict, id):  # @ReservedAssignment
        """ Use :py:meth:`RangeDictionary.view_factory` to create views
        """
        # print("Single")
        super(_SingleView, self).__init__(range_dict)
        self._id = id

    def __str__(self):
        return "View with ID: {}".format(self._id)

    @overrides(AbstractDict.ids)
    def ids(self):
        return [self._id]

    @overrides(AbstractDict.get_value)
    def get_value(self, key):
        return self._range_dict.get_list(key).get_value_by_id(id=self._id)

    @overrides(AbstractDict.iter_all_values)
    def iter_all_values(self, key, update_save=False):
        if isinstance(key, str):
            yield self._range_dict.get_list(key).get_value_by_id(id=self._id)
        else:
            yield self._range_dict.get_values_by_id(key=key, id=self._id)

    @overrides(AbstractDict.set_value)
    def set_value(self, key, value):
        return self._range_dict.get_list(key).set_value_by_id(
            value=value, id=self._id)

    @overrides(AbstractDict.iter_ranges)
    def iter_ranges(self, key=None):
        return self._range_dict.iter_ranges_by_id(key=key, id=self._id)
