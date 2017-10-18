from spinn_utilities.lazy.ranged_list import RangedList
from spinn_utilities.lazy.single_view import SingleView
from spinn_utilities.lazy.slice_view import SliceView
from spinn_utilities.lazy.ids_view import IdsView
from spinn_utilities.lazy.abstract_dict import AbstractDict
from spinn_utilities.lazy.multiple_values_exception import \
    MultipleValuesException


class RangeDictionary(AbstractDict):

    def __init__(self, size, defaults):
        self._size = size
        self._value_lists = dict()
        for key, value in defaults.items():
            self._value_lists[key] = RangedList(size, value)

    def _view_factory(self, ids):
        if not all(isinstance(x, int) for x in ids):
            raise KeyError("Only list/tuple of int are supported")
        if len(ids) == 1:
            return SingleView(range_dict=self, id=ids[0])
        ids = list(ids)
        ids.sort()
        if len(ids) == ids[-1] - ids[0] + 1:
            return SliceView(range_dict=self, start=ids[0], stop=ids[-1] + 1)
        else:
            return IdsView(range_dict=self, ids=ids)

    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.start == key.stop:
                return SingleView(range_dict=self, id=key.start)
            elif key.step is None or key.step == 1:
                return SliceView(range_dict=self, start=key.start,
                                 stop=key.stop)
            else:
                ids = range(self._size)[key]
                return self._view_factory(ids=ids)
        elif isinstance(key, int):
            return SingleView(range_dict=self, id=key)
        elif isinstance(key, str):
            return self.get_value_all(key)
        elif (isinstance(key, (tuple, list))):
            return self._view_factory(ids=key)
        else:
            raise KeyError("Unexpected key type: {}".format(type(key)))

    def get_value_all(self, key):
        return self._value_lists[key].get_value_all()

    def get_value_by_id(self, key, id):
        return self._value_lists[key].get_value_by_id(id=id)

    def get_value_by_slice(self, key, start, stop):
        return self._value_lists[key].get_value_by_slice(
            slice_start=start, slice_stop=stop)

    def get_value_by_ids(self, key, ids):
        return self._value_lists[key].get_value_by_ids(ids=ids)

    def set_value(self, key, value):
        self._value_lists[key].set_value(value)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            return self.set_value(key=key, value=value)
        if isinstance(key, (slice, int, tuple, list)):
            raise KeyError("Settting of a slice/ids not supported")
        else:
            raise KeyError("Unexpected key type: {}".format(type(key)))

    def set_value_by_id(self, key, id, value):
        self._value_lists[key].set_value_by_id(id=id, value=value)

    def set_value_by_slice(self, key, start, stop, value):
        return self._value_lists[key].set_value_by_slice(
            slice_start=start, slice_stop=stop, value=value)

    def items(self):
        results = []
        for key in self.keys():
            value = self.get_value_all(key)
            results.append((key, value))
        return results

    def iteritems(self):
        return iter(self.items())

    def values(self):
        results = []
        for key in self.keys():
            value = self.get_value_all(key)
            results.append(value)
        return results

    def itervalues(self):
        return iter(self.values())

    def ids(self):
        return range(self._size)

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
