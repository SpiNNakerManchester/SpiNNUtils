from spinn_utilities.ranged.abstract_view import AbstractView


class _SingleView(AbstractView):

    def __init__(self, range_dict, id):  # @ReservedAssignment
        """
        USE RangeDictionary.view_factory to create views
        """
        print "Single"
        AbstractView.__init__(self, range_dict)
        self._id = id

    def __str__(self):
        return "View with id: {}".format(self._id)

    def ids(self):
        return [self._id]

    def get_value(self, key):
        return self._range_dict.get_list(key).get_value_by_id(id=self._id)

    def iter_all_values(self, key, update_save=False):
        if isinstance(key, str):
            yield self._range_dict.get_list(key).get_value_by_id(id=self._id)
        else:
            yield self._range_dict.get_values_by_id(key=key, id=self._id)

    def set_value(self, key, value):
        return self._range_dict.get_list(key).set_value_by_id(
            value=value, id=self._id)

    def iter_ranges(self, key):
        return self._range_dict.iter_ranges_by_id(key=key, id=self._id)
