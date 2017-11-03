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

        key is a str is currently not supported use get_value instead. \
        In the future this may be supported to return some kind of list\
        (AbstractList) but how to handle a view there to be determined

        For int and int collections a new view will be returned using\
        RangeDictionary.view_factory

        NOTE int are indexes into the list of ids not id values\
        So for a view with ids [2,3,4,5] view[2] will have an id of 4

        :param key: str, int or collection of int
        :return: the single value for the str key or a view
        :raises MultipleValuesException If the keys has multiple values set.\
            But not if other keys not asked for have multiple values
        """
        if isinstance(key, str):
            raise KeyError("view[key] is not supported Use get_value() ")
        ids = self.ids()
        if isinstance(key, (slice, int)):
            return self._range_dict.view_factory(ids[key])
        selected = []
        for i in key:
            selected.append(ids[i])
        return self._range_dict.view_factory(selected)

    def __setitem__(self, key, value):
        """
        See AbstractDict.set_value

        Note: Unlike __getitem__ int based ids are NOT supported so\
        view[int] == will raise and exception

        """
        if isinstance(key, str):
            return self.set_value(key=key, value=value)
        if isinstance(key, (slice, int, tuple, list)):
            raise KeyError("Setting of a slice/ids not supported")
        else:
            raise KeyError("Unexpected key type: {}".format(type(key)))

    def viewkeys(self):
        return self._range_dict.viewkeys()

    def set_default(self, key, default):
        self._range_dict.set_default(key, default)

    def get_default(self, key):
        self._range_dict.get_default(key)

    def keys(self):
        return self._range_dict.keys()
