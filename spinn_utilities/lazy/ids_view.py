from spinn_utilities.lazy.abstract_view import AbstractView


class IdsView(AbstractView):

    def __init__(self, range_dict, ids):
        AbstractView.__init__(self, range_dict)
        self._ids = ids

    def __str__(self):
        return "View with ids: {}".format(self._ids)

    def ids(self):
        return list(self._ids)

    def get_value(self, key):
        return self._range_dict.get_value_by_ids(key, self._ids)

    def set_value(self, key):
        self._range_dict.set_value_by_ids(key, self._ids)

