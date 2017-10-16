from spinn_utilities.lazy.abstract_view import AbstractView


class SingleView(AbstractView):

    def __init__(self, range_dict, id):
        AbstractView.__init__(self, range_dict)
        self._id = id

    def __str__(self):
        return "View with id: {}".format(self._id)

    def ids(self):
        return [self._id]

    def get_value(self, key):
        return self._range_dict.get_value_by_id(key, self._id)

