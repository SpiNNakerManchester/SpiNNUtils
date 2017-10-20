from spinn_utilities.ranged.ranged_list import RangedList
from spinn_utilities.ranged.single_view import _SingleView
from spinn_utilities.ranged.slice_view import _SliceView
from spinn_utilities.ranged.ids_view import _IdsView
from spinn_utilities.ranged.abstract_dict import AbstractDict
from spinn_utilities.ranged.multiple_values_exception import \
    MultipleValuesException


class RangeDictionary(AbstractDict):

    def __init__(self, size, defaults):
        self._size = size
        self._value_lists = dict()
        for key, value in defaults.items():
            self._value_lists[key] = RangedList(size, value)

    def view_factory(self, key):
        if isinstance(key, int):
            return _SingleView(range_dict=self, id=key)
        if isinstance(key, slice):
            if key.start == key.stop:
                return _SingleView(range_dict=self, id=key.start)
            elif key.step is None or key.step == 1:
                return _SliceView(range_dict=self, start=key.start,
                                  stop=key.stop)
            else:
                key = range(self._size)[key]
        if not all(isinstance(x, int) for x in key):
            raise KeyError("Only list/tuple of int are supported")
        if len(key) == 1:
            return _SingleView(range_dict=self, id=key[0])
        key = list(key)
        key.sort()
        if len(key) == key[-1] - key[0] + 1:
            return _SliceView(range_dict=self, start=key[0], stop=key[-1] + 1)
        else:
            return _IdsView(range_dict=self, ids=key)

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.get_value(key)
        if (isinstance(key, (int, slice, tuple, list))):
            return self.view_factory(key=key)
        else:
            raise KeyError("Unexpected key type: {}".format(type(key)))

    def get_value(self, key):
        return self._value_lists[key].get_value_all()

    def iter_values(self, key, fast=True):
        if fast:
            return self._value_lists[key].__iter__()
        else:
            return self._value_lists[key].iter()

    def get_value_by_id(self, key, id):
        return self._value_lists[key].get_value_by_id(id=id)

    def get_value_by_slice(self, key, start, stop):
        return self._value_lists[key].get_value_by_slice(
            slice_start=start, slice_stop=stop)

    def iter_values_by_slice(self, key, start, stop):
        return self._value_lists[key].slice_iter(
            slice_start=start, slice_stop=stop)

    def iter_values_by_ids(self, key, ids):
        return self._value_lists[key].iter_by_ids(ids=ids)

    def get_value_by_ids(self, key, ids):
        return self._value_lists[key].get_value_by_ids(ids=ids)

    def set_value(self, key, value):
        self._value_lists[key].set_value(value)

    def __setitem__(self, key, value):
        print "set"
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

    def set_value_by_ids(self, key, ids, value):
        for id in ids:
            self._value_lists[key].set_value_by_id(id=id, value=value)

    def items(self):
        results = []
        for key in self.keys():
            value = self.get_value(key)
            results.append((key, value))
        return results

    def iteritems(self):
        return iter(self.items())

    def values(self):
        results = []
        for key in self.keys():
            value = self.get_value(key)
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
