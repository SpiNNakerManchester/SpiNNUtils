from spinn_utilities.lazy.ranged_list import RangedList
from spinn_utilities.lazy.single_view import SingleView
from spinn_utilities.lazy.range_view import RangeView
from spinn_utilities.lazy.ids_view import IdsView
from spinn_utilities.lazy.multiple_values_exception import \
    MultipleValuesException


class RangeDictionary(object):

    def __init__(self, size, defaults):
        self._size = size
        self._value_lists = dict()
        for key, value in defaults.items():
            self._value_lists[key] = RangedList(size, value)
        print self._value_lists

    def _view_factory(self, ids):
        if not all(isinstance(x, int) for x in ids):
            raise KeyError("Only list/tuple of int are supported")
        if len(ids) == 1:
            return SingleView(self, ids[0])
        ids = list(ids)
        ids.sort()
        if len(ids) == ids[-1] - ids[0] + 1:
            return RangeView(self, ids[0], ids[1] + 1)
        else:
            return IdsView(self, ids)

    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.start == key.stop:
                return SingleView(self, key.start)
            elif key.step is None or key.step == 1:
                return RangeView(self, key.start, key.stop)
            else:
                ids = range(self._size)[key]
                return self._view_factory(ids)
        elif isinstance(key, int):
            return SingleView(self, key)
        elif isinstance(key, str):
            return self.get_value(key)
        elif (isinstance(key, (tuple, list))):
            return self._view_factory(key)
        else:
            print key
            raise KeyError("Unexpected key type: {}".format(type(key)))

    def get_value(self, key):
        possible = set(self._value_lists[key])
        if len(possible) == 1:
            return possible.pop()
        raise MultipleValuesException(key, possible.pop(), possible.pop())

    def get_value_by_id(self, key, id):
        return self._value_lists[key].get_data(id)

    def get_value_by_range(self, key, start, stop):
        return self._value_lists[key].get_data_by_range(start, stop)

    def ids(self):
        return range(self._size)

    def __contains__(self, key):
        return key in self._value_lists

    def has_key(self, key):
        return self._value_lists.has_key(key)

    def keys(self):
        return self._value_lists.keys()

    def iterkeys(self):
        return self._value_lists.iterkeys()

    def viewkeys(self):
        return self._value_lists.viewkeys()

    def setdefault(self, key, default=None):
        return self._value_lists[key].setdefault(default)
