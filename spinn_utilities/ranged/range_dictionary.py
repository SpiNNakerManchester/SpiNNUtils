from spinn_utilities.ranged.ranged_list import RangedList
from spinn_utilities.ranged.single_view import _SingleView
from spinn_utilities.ranged.slice_view import _SliceView
from spinn_utilities.ranged.ids_view import _IdsView
from spinn_utilities.ranged.abstract_dict import AbstractDict


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
            if key.start is None:
                slice_start = 0
            else:
                slice_start = key.start
            if key.stop is None:
                slice_stop = self._size
            else:
                slice_stop = key.stop
            if slice_start == slice_stop:
                return _SingleView(range_dict=self, id=slice_start)
            elif key.step is None or key.step == 1:
                return _SliceView(range_dict=self, start=slice_start,
                                  stop=slice_stop)
            else:
                key = range(self._size)[key]
        if not all(isinstance(x, int) for x in key):
            raise KeyError("Only list/tuple of int are supported")
        if len(key) == 1:
            return _SingleView(range_dict=self, id=key[0])
        key = list(key)
        if len(key) == key[-1] - key[0] + 1:
            in_order = sorted(key)
            if in_order == key:
                return _SliceView(
                    range_dict=self, start=key[0], stop=key[-1] + 1)
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
        if isinstance(key, str):
            return self._value_lists[key].get_value_all()
        if key is None:
            key = self.keys()
        results = dict()
        for a_key in key:
            results[a_key] = self._value_lists[a_key].get_value_all()
        return results

    def get_values_by_id(self, key, id):
        if isinstance(key, str):
            return self._value_lists[key].get_value_by_id(id)
        if key is None:
            key = self.keys()
        results = dict()
        for a_key in key:
            results[a_key] = self._value_lists[a_key].get_value_by_id(id)
        return results

    def get_list(self, key):
        return self._value_lists[key]

    def update_save_iter_all_values(self, key, ids):
        for id in ids:
            yield self.get_values_by_id(key=key, id=id)

    def iter_all_values(self, key=None, update_save=True):
        if isinstance(key, str):
            if update_save:
                return self._value_lists[key].iter()
            else:
                return self._value_lists[key].__iter__()
        else:
            if update_save:
                return self.update_save_iter_all_values(key, range(self._size))
            else:
                return self._values_from_ranges(self.iter_ranges(key))

    def iter_values_by_slice(
            self, slice_start, slice_stop, key=None, update_save=False):
        if update_save:
            return self.update_save_iter_all_values(
                key, range(slice_start, slice_stop))
        else:
            return self._values_from_ranges(self.iter_ranges_by_slice(
                slice_start=slice_start, slice_stop=slice_stop, key=key))

    def iter_values_by_ids(self, ids, key=None, update_save=True):
        if update_save:
            return self.update_save_iter_all_values(key, ids)
        else:
            return self._values_from_ranges(self.iter_ranges_by_ids(
                key=key, ids=ids))

    def _values_from_ranges(self, ranges):
        for (start, stop, value) in ranges:
            for _ in range(start, stop):
                yield value

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
        return key in self._value_lists

    def keys(self):
        return self._value_lists.keys()

    def iterkeys(self):
        return self._value_lists.iterkeys()

    def viewkeys(self):
        return self._value_lists.viewkeys()

    def setdefault(self, key, default=None):
        return self._value_lists[key].setdefault(default)

    def _merge_ranges(self, range_iters):
        current = dict()
        ranges = dict()
        start = 0
        stop = self._size
        keys = range_iters.keys()
        for key in keys:
            ranges[key] = range_iters[key].next()
            start = ranges[key][0]
            current[key] = ranges[key][2]
            stop = min(ranges[key][1], stop)
        yield (start, stop, current)
        while stop < self._size:
            current = dict()
            start = self._size
            next_stop = self._size
            for key in keys:
                if ranges[key][1] == stop:
                    ranges[key] = range_iters[key].next()
                start = min(max(ranges[key][0], stop), start)
                next_stop = min(ranges[key][1], next_stop)
                current[key] = ranges[key][2]
            stop = next_stop
            yield (start, stop, current)

    def iter_ranges(self, key=None):
        if isinstance(key, str):
            return self._value_lists[key].iter_ranges()
        if key is None:
            key = self.keys()
        ranges = dict()
        for a_key in key:
            ranges[a_key] = self._value_lists[a_key].iter_ranges()
        return self._merge_ranges(ranges)

    def iter_ranges_by_id(self, key=None, id=None):
        if isinstance(key, str):
            return self._value_lists[key].iter_ranges_by_id(id=id)
        if key is None:
            key = self.keys()
        ranges = dict()
        for a_key in key:
            ranges[a_key] = self._value_lists[a_key].iter_ranges_by_id(id=id)
        return self._merge_ranges(ranges)

    def iter_ranges_by_slice(self, key, slice_start, slice_stop):
        if isinstance(key, str):
            return self._value_lists[key].iter_ranges_by_slice(
                slice_start=slice_start, slice_stop=slice_stop)
        if key is None:
            key = self.keys()
        ranges = dict()
        for a_key in key:
            ranges[a_key] = self._value_lists[a_key].iter_ranges_by_slice(
                slice_start=slice_start, slice_stop=slice_stop)
        return self._merge_ranges(ranges)

    def iter_ranges_by_ids(self, ids, key=None):
        if isinstance(key, str):
            return self._value_lists[key].iter_ranges_by_ids(ids=ids)
        if key is None:
            key = self.keys()
        ranges = dict()
        for a_key in key:
            ranges[a_key] = self._value_lists[a_key].\
                iter_ranges_by_ids(ids=ids)
        return self._merge_ranges(ranges)
