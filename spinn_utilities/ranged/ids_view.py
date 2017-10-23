from spinn_utilities.ranged.abstract_view import AbstractView


class _IdsView(AbstractView):

    def __init__(self, range_dict, ids):
        """
        USE RangeDictionary.view_factory to create views
        """
        AbstractView.__init__(self, range_dict)
        self._ids = ids

    def __str__(self):
        return "View with ids: {}".format(self._ids)

    def ids(self):
        return list(self._ids)

    def get_value(self, key):
        return self._range_dict.get_value_by_ids(key, self._ids)

    def set_value(self, key, value):
        self._range_dict.set_value_by_ids(key=key, ids=self._ids, value=value)

    def iter_all_values(self, key, fast=True):
        return self._range_dict.iter_values_by_ids(key=key, ids=self._ids)
