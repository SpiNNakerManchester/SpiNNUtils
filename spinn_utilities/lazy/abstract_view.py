from spinn_utilities.lazy.abstract_dict import AbstractDict


class AbstractView(AbstractDict):

    # self.get_value(key)

    # self.set_value(key, value)

    # self.ids()

    def __init__(self, range_dict):
        self._range_dict = range_dict

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.get_value(key)
        ids = self.ids()
        if isinstance(key, (slice, int)):
            return self._range_dict._view_factory(ids[key])
        if isinstance(key, (tuple, list)):
            selected = []
            for i in key:
                selected.append(ids[i])
            return self._range_dict._view_factory(selected)
        else:
            raise KeyError("Unexpected key type: {}".format(type(key)))

    def __setitem__(self, key, value):
        if isinstance(key, str):
            return self.set_value(key=key, value=value)
        if isinstance(key, (slice, int, tuple, list)):
            raise KeyError("Settting of a slice/ids not supported")
        else:
            raise KeyError("Unexpected key type: {}".format(type(key)))

    def __contains__(self, key):
        return self._range_dict.__contains__(key)

    def has_key(self, key):
        return self._range_dict.has_key(key)

    def keys(self):
        return self._range_dict.keys()

    def iterkeys(self):
        return self._range_dict.iterkeys()

    def viewkeys(self):
        return self._range_dict.viewkeys()

    def items(self):
        results = []
        for key in self._range_dict.keys():
            value = self.get_value(key)
            results.append((key, value))
        return results

    def iteritems(self):
        return iter(self.items())

    def values(self):
        results = []
        for key in self._range_dict.keys():
            value = self.get_value(key)
            results.append(value)
        return results

    def itervalues(self):
        return iter(self.values())

    def setdefault(self, key, default=None):
        self._range_dict.setdefault(key, default)