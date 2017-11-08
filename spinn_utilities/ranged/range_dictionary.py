from spinn_utilities.ranged.ranged_list import RangedList
from spinn_utilities.ranged.abstract_list import AbstractList
from spinn_utilities.ranged.single_view import _SingleView
from spinn_utilities.ranged.slice_view import _SliceView
from spinn_utilities.ranged.ids_view import _IdsView
from spinn_utilities.ranged.abstract_dict import AbstractDict
from spinn_utilities.ranged.abstract_sized import AbstractSized


class RangeDictionary(AbstractDict, AbstractSized):
    """
    Main holding class for a range of similar Dictionary object.

    Keys in the dictionary must be str object and can not be removed.

    New keys can be added using the dict[str] = xyz format

    The size (length of the list) is fixed and set at init time.
    """

    def __init__(self, size, defaults=None):
        """
        Main constructor for a Ranged Dictionary

        The Object is set up initially where every id in the range will share
        the same value for each key.
        All keys must be or type str
        The default Values can be anything including None

        :param size: Fixed number of ids/ Length of lists
        :type size: int
        :param defaults: Default dictionary where all keys must be str
        :type defaults: dict
        """
        AbstractSized.__init__(self, size)
        self._value_lists = dict()
        if defaults is not None:
            for key, value in defaults.items():
                self._value_lists[key] = RangedList(
                    size=size, value=value, key=key)

    def view_factory(self, key):
        """
        Main function for creating views.

        This is the preferred way of creating new views as it check parameters
        and returns the most efficient view.

        Note the __getitem__ methods called by Object[id] and similar deffer
        to this method so are fine to use.

        The id(s) used are the actual ids in the Range and not indexes on
        the list of ids

        :param key: A single int id, a Slice object or an Iterable of int ids
        :return: A view over the Range
        """
        if isinstance(key, int):
            self._check_id(key)
            return _SingleView(range_dict=self, id=key)
        if isinstance(key, slice):
            slice_start, slice_stop = self._check_slice(
               key.start, key.stop)
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
        """
        Support for the view[x] based the type of the key

        If key is a str a list type object of AbstractList is returned

        Otherwise a View (AbstractView) over part of the ids in the Dict is\
        returned

        Multiple str object or None are not supported as keys here

        :param key: a str, int, iterable of int values
        :return: An AbstractList or AbstractView
        """
        if isinstance(key, str):
            return self._value_lists[key]
        else:
            return self.view_factory(key=key)

    def get_value(self, key=None):
        """
        See AbstractDict
        """
        if isinstance(key, str):
            return self._value_lists[key].get_value_all()
        if key is None:
            key = self.keys()
        results = dict()
        for a_key in key:
            results[a_key] = self._value_lists[a_key].get_value_all()
        return results

    def get_values_by_id(self, key, id):  # @ReservedAssignment
        """
        Same as AbstractDict.get_value but limited to a single id

        :param key: as AbstractDict.get_value
        :param id: single int id
        :return: See AbstractDict.get_value
        """
        if isinstance(key, str):
            return self._value_lists[key].get_value_by_id(id)
        if key is None:
            key = self.keys()
        results = dict()
        for a_key in key:
            results[a_key] = self._value_lists[a_key].get_value_by_id(id)
        return results

    def get_list(self, key):
        """
        Gets the storage unit for a single key.

        Mainly intended by Views to access the data for one key directly

        :param key: str which must be a key in the dict
        :rtype RangedList
        """
        return self._value_lists[key]

    def update_safe_iter_all_values(self, key, ids):
        """
        Same as AbstractDict.iter_all_values
        but limited to a collection of ids and update safe

        """
        for id in ids:  # @ReservedAssignment
            yield self.get_values_by_id(key=key, id=id)

    def iter_all_values(self, key=None, update_save=False):
        """
        See AbstractDict.iter_all_values
        """
        if isinstance(key, str):
            if update_save:
                return self._value_lists[key].iter()
            else:
                return self._value_lists[key].__iter__()
        else:
            if update_save:
                return self.update_safe_iter_all_values(
                    key, xrange(self._size))
            else:
                return self._values_from_ranges(self.iter_ranges(key))

    def iter_values_by_slice(
            self, slice_start, slice_stop, key=None, update_save=False):
        """
        Same as AbstractDict.iter_all_values
        but limited to a simple slice

        """
        if isinstance(key, str) and not update_save:
            return self._value_lists[key].iter_by_slice(
                self, slice_start=slice_start, slice_stop=slice_stop)
        if update_save:
            return self.update_safe_iter_all_values(
                key, xrange(slice_start, slice_stop))
        else:
            return self._values_from_ranges(self.iter_ranges_by_slice(
                slice_start=slice_start, slice_stop=slice_stop, key=key))

    def iter_values_by_ids(self, ids, key=None, update_save=False):
        """
        Same as AbstractDict.iter_all_values
        but limited to a simple slice

        """
        if update_save:
            return self.update_safe_iter_all_values(key, ids)
        else:
            return self._values_from_ranges(self.iter_ranges_by_ids(
                key=key, ids=ids))

    def _values_from_ranges(self, ranges):
        for (start, stop, value) in ranges:
            for _ in xrange(start, stop):
                yield value

    def set_value(self, key, value):
        """
        see AbstractDict.set_value

        """
        self._value_lists[key].set_value(value)

    def __setitem__(self, key, value):
        """
        Wrapper around set_value to support range["key"] =

        NOTE: range[int] = is not supported

        value can be a single object or None in\
        which case every value in the list is set to that.
        value can be a collection but\
        then it must be exactly the size of all lists in this dictionary.
        value can be an AbstractList

        :param key: Existing or NEW str dictionary kay
        :type key: str
        :param value: List or value to create list based on
        :return:
        """
        if isinstance(key, str):
            if key in self:
                self.set_value(key=key, value=value)
            else:
                if isinstance(value, AbstractList):
                    assert self._size == value._size
                    self._value_lists[key] = value
                else:
                    new_list = RangedList(size=self._size, value=value,
                                          key=key)
                    self._value_lists[key] = new_list
        elif isinstance(key, (slice, int, tuple, list)):
            raise KeyError("Settting of a slice/ids not supported")
        else:
            raise KeyError("Unexpected key type: {}".format(type(key)))

    def ids(self):
        """
        Returns a list of the ids in this Range
        :return:a list of the ids in this Range
        :rtype list(int)
        """
        return range(self._size)

    def has_key(self, key):
        return key in self._value_lists

    def keys(self):
        return self._value_lists.keys()

    def iterkeys(self):
        return self._value_lists.iterkeys()

    def viewkeys(self):
        return self._value_lists.viewkeys()

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
        """
        See AbstractDict.iter_ranges
        """
        if isinstance(key, str):
            return self._value_lists[key].iter_ranges()
        if key is None:
            key = self.keys()
        ranges = dict()
        for a_key in key:
            ranges[a_key] = self._value_lists[a_key].iter_ranges()
        return self._merge_ranges(ranges)

    def iter_ranges_by_id(self, key=None, id=None):  # @ReservedAssignment
        """
        Same AbstractDict.iter_ranges but limited to one id

        :param key: see AbstractDict.iter_ranges param key
        :param id: single id which is the actual id and not an index into ids
        :type id: int
        """
        if isinstance(key, str):
            return self._value_lists[key].iter_ranges_by_id(id=id)
        if key is None:
            key = self.keys()
        ranges = dict()
        for a_key in key:
            ranges[a_key] = self._value_lists[a_key].iter_ranges_by_id(id=id)
        return self._merge_ranges(ranges)

    def iter_ranges_by_slice(self, key, slice_start, slice_stop):
        """
        Same AbstractDict.iter_ranges but limited to a simple slice

        slice_start amd slice_stop are actual id values and
        not indexes into the ids
        They must also be actual values, so None, maxint, and\
        negative numbers are not supported.

        :param key: see AbstractDict.iter_ranges param key
        :param slice_start: Inclusive ie first id
        :param slice_stop:  Exclusive to last id + 1
        :return: see AbstractDict.iter_ranges
        """
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
        """
         Same AbstractDict.iter_ranges but limited to a collection of ids

         ids are actual id values and not indexes into the ids

         :param key: see AbstractDict.iter_ranges param key
         :param ids: Collection of ids in the range
         :return: see AbstractDict.iter_ranges
         """
        if isinstance(key, str):
            return self._value_lists[key].iter_ranges_by_ids(ids=ids)
        if key is None:
            key = self.keys()
        ranges = dict()
        for a_key in key:
            ranges[a_key] = self._value_lists[a_key].\
                iter_ranges_by_ids(ids=ids)
        return self._merge_ranges(ranges)

    def set_default(self, key, default):
        """
        Sets the default value for a single key.

        Note: Does not change any values
        but only changes what reset_value would do

        WARNING: If called on a View it sets the default for the WHOLE range
        and not just the view.

        :param key: Existing dict key
        :type key: str
        :param default: Value to be used by reset
        """
        self._value_lists[key].set_default(default)

    def get_default(self, key):
        """
        See AbstractDict.get_default
        """
        return self._value_lists[key].get_default()
