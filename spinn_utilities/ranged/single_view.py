from spinn_utilities.ranged.abstract_view import AbstractView


class _SingleView(AbstractView):

    def __init__(self, range_dict, id):
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
        return self._range_dict.get_value_by_id(key=key, id=self._id)

    def iter_values(self, key, fast=True):
        yield self._range_dict.get_value_by_id(key=key, id=self._id)

    def set_value(self, key, value):
        return self._range_dict.set_value_by_id(key=key, value=value,
                                                id=self._id)
