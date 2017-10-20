from spinn_utilities.ranged.abstract_dict import AbstractDict


class AbstractView(AbstractDict):

    def __init__(self, range_dict):
        """
        USE RangeDictionary.view_factory to create views
        """
        self._range_dict = range_dict

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.get_value(key)
        ids = self.ids()
        if isinstance(key, (slice, int)):
            return self._range_dict.view_factory(ids[key])
        if isinstance(key, (tuple, list)):
            selected = []
            for i in key:
                selected.append(ids[i])
            return self._range_dict.view_factory(selected)
        raise KeyError("Unexpected key type: {}".format(type(key)))

    def __setitem__(self, key, value):
        if isinstance(key, str):
            return self.set_value(key=key, value=value)
        if isinstance(key, (slice, int, tuple, list)):
            raise KeyError("Settting of a slice/ids not supported")
        else:
            raise KeyError("Unexpected key type: {}".format(type(key)))

    def viewkeys(self):
        return self._range_dict.viewkeys()

    def setdefault(self, key, default=None):
        self._range_dict.setdefault(key, default)

    def keys(self):
        return self._range_dict.keys()

