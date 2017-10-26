from spinn_utilities.ranged.abstract_dict import AbstractDict


class AbstractView(AbstractDict):

    def __init__(self, range_dict):
        """
        USE RangeDictionary.view_factory to create views
        """
        self._range_dict = range_dict

    def __getitem__(self, key):
        """
        Support for the view[x] based the type of the key

        For str key values see AbstractDict.get_value
        For multiple str keys (including None for all) use get_value

        For int and int collections a new view will be returned using
        RangeDictionary.view_factory

        NOTE int are indexes into the list of ids not id values
        So for a view with ids [2,3,4,5] view[2] will have an id of 4

        :param key: str, int or collection of int
        :return: the single value for the str key or a view
        :raises MultipleValuesException If the keys has multiple values set.
            But not if other keys not asked for have multiple values
        """
        if isinstance(key, str):
            return self.get_value(key)
        ids = self.ids()
        if isinstance(key, (slice, int)):
            return self._range_dict.view_factory(ids[key])
        if isinstance(key, (tuple, list, set)):
            selected = []
            for i in key:
                selected.append(ids[i])
            return self._range_dict.view_factory(selected)
        raise KeyError("Unexpected key type: {}".format(type(key)))

    def __setitem__(self, key, value):
        """
        See AbstractDict.set_value

        Note: Unlike __getitem__ int based ids are NOT supported so
        view[int] == will raise and exception

        """
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
