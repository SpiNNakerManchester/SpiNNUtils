from spinn_utilities.ranged.abstract_view import AbstractView


class _SliceView(AbstractView):

    def __init__(self, range_dict, start, stop):
        """
        USE RangeDictionary.view_factory to create views
        """
        AbstractView.__init__(self, range_dict)
        self._start = start
        self._stop = stop

    def __str__(self):
        return "View with range: {} to {}".format(self._start, self._stop)

    def ids(self):
        return range(self._start, self._stop)

    def get_value(self, key):
        return self._range_dict.get_list(key).get_value_by_slice(
            slice_start=self._start, slice_stop=self._stop)

    def _aware_iter(self, key):
        ranged_list = self._range_dict.get_list(key)
        for id in self.ids():
            yield ranged_list.get_value_by_id(id=id)

    def iter_all_values(self, key, fast=True):
        if fast:
            return self._range_dict.iter_values_by_slice(
                key=key, start=self._start, stop=self._stop)
        return self._aware_iter(key)

    def set_value(self, key, value):
        self._range_dict.get_list(key).set_value_by_slice(
            slice_start=self._start, slice_stop=self._stop, value=value)

    def iter_ranges(self, key):
        return self._range_dict.iter_ranges_by_slice(
            key=key, slice_start=self._start, slice_stop=self._stop)

