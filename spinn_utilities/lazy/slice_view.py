from spinn_utilities.lazy.abstract_view import AbstractView


class SliceView(AbstractView):

    def __init__(self, range_dict, start, stop):
        AbstractView.__init__(self, range_dict)
        self._start = start
        self._stop = stop

    def __str__(self):
        return "View with range: {} to {}".format(self._start, self._stop)

    def ids(self):
        return range(self._start, self._stop)

    def get_value(self, key):
        return self._range_dict.get_value_by_slice(key=key, start=self._start,
                                                   stop=self._stop)

    def set_value(self, key, value):
        self._range_dict.set_value_by_slice(key=key, start=self._start,
                                            stop=self._stop, value=value)
