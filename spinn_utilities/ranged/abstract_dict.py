from six import add_metaclass

from spinn_utilities.abstract_base import AbstractBase, abstractmethod


@add_metaclass(AbstractBase)
class AbstractDict(object):
    """
    Base class for the RangedDictionary and ALL views

    This allows the users to not have to worry if they have a view.
    """

    @abstractmethod
    def get_value(self, key):
        """
        Gets a single shared value for all ids covered by this view

        :param key: The key or keys to get the value of. Use None for all
        :type key: str, iterable of str, or None
        :return: If key is a str this returns the single object.
            If key is iterable (list, tuple, set, etc) of str (or None)\
            returns a dictionary object
        :raises MultipleValuesException If even one of the keys has multiple\
            values set.
            But not if other keys not asked for have multiple values
        """
        pass

    @abstractmethod
    def set_value(self, key, value):
        """
        Resets a already existing key to the new value

        All ids in the whole range or view will have this key set

        WARNING: This method does not allow adding keys.
        The dict[str] = will add a new key but is not supported for views

        WARNING: If a View is created over multiple ranges this method would\
            raise a KeyError if any the ranges does not have the key.\
            (Currently multiple ranges not yet supported)

        :param key: key to value being set
        :type key: str
        :param value: any object
        :raise KeyError: If a new key is being used.
        """
        pass

    @abstractmethod
    def iterids(self):
        """
        Returns an iterator over the ids in range or view.

        :return: Generator of ids
        """
        pass

    def ids(self):
        """
        Returns the ids in range or view.

        If the view is setup with ids out of numerical order the order used\
        to create the view is maintained.

        WARNING: If indexing into a view you are picking the X'th id.\
        So if the ids are [2,3,4,5] the view[2] will be the data for id 4\
        and not 2

        :return: list of ids
        :rtype: list(int)

        """
        return list(self.iterids())

    @abstractmethod
    def has_id(self, id_value):
        """
        Returns True if the given ID is in the range or view

        :rtype: bool
        """

    @abstractmethod
    def iter_all_values(self, key, update_save=False):
        """
        Iterates over the value(s) for all ids covered by this view

        There will be one yield for each id even if values are repeated.

        :param key: The key or keys to get the value of. Use None for all
        :type key: str, iterable of str, or None
            None is assumed to mean all keys.
        :param update_save: If set True the iteration will work even if values\
            are updated during iteration. If left False the iterator may be\
            faster but behaviour is UNDEFINED and UNCHECKED if ANY values are\
            changed during iteration.
        :return: If key is a str this yields single objects.
            If key is iterable (list, tuple, set, etc) of str (or None)\
            yields dictionary objects
        """
        pass

    def get_ranges(self, key=None):
        """
        Lists the ranges(s) for all ids covered by this view

        There will be one yield for each range which may cover one or\
        more ids.

        Note: As the data is created in a single call this is not affected\
        by any updates.

        :param key: The key or keys to get the value of. Use None for all
        :type key: str, iterable of str, or None
        :return: List of tuples of (start, stop, value)
            start is INCLUSIVE so is the first id in the range
            stop is EXCLUSIVE so is the last id in the range + 1
            If key is a str this value is a single object.
            If key is iterable (list, tuple, set, etc) of str (or None) \
            value is a dictionary object
        """
        return list(self.iter_ranges(key=key))

    @abstractmethod
    def iter_ranges(self, key=None):
        """
        Iterates over the ranges(s) for all ids covered by this view

        There will be one yield for each range which may cover one or\
        more ids.

        WARNING: This iterator is NOT update safe!\
            Behaviour is UNDEFINED and UNCHECKED if ANY values are\
            changed during iteration.

        :param key: The key or keys to get the value of. Use None for all
        :type key: str, iterable of str, or None
        :return: yields tuples of (start, stop, value)
            start is INCLUSIVE so is the first id in the range
            stop is EXCLUSIVE so is the last id in the range + 1
            If key is a str this value is a single object.
            If key is iterable (list, tuple, set, etc) of str (or None)\
            value is a dictionary object
        """
        pass

    @abstractmethod
    def get_default(self, key):
        """
        Gets the default value for a single key.

        Unless changed the default is the original value

        Note: Does not change any values\
        but only changes what reset_value would do

        :param key: Existing dict key
        :type key: str
        :return: default for this key.
        """
        pass

    def items(self):
        """
        Returns a list of (key, value) tuples

        Works only if the whole ranges/view has single values.

        If key is a str the values are single objects.
        If key is iterable (list, tuple, set, etc) of str (or None)\
        values are dictionary objects

        :return: List of (key, value) tuples
        :raises MultipleValuesException If even one of the keys has multiple\
            values set.
        """
        results = []
        for key in self.iterkeys():
            value = self.get_value(key)
            results.append((key, value))
        return results

    def iteritems(self):
        """
        Iterates over the (key, value) tuples

        Works only if the whole ranges/view has single values.

        If key is a str the values are single objects.
        If key is iterable (list, tuple, set, etc) of str (or None)\
        values are dictionary objects

        This function is safe for value updates but may miss new keys\
        added during iteration.

        :return: yield (key, value) tuples
        :raises MultipleValuesException If even one of the keys has multiple\
            values set.
        """
        for key in self.iterkeys():
            yield (key, self.get_value(key))

    def values(self):
        """
        Returns a list of value

        Works only if the whole ranges/view has single values.

        If key is a str the values are single objects.
        If key is iterable (list, tuple, set, etc) of str (or None)\
        values are dictionary objects

        :return: List of values
        :raises MultipleValuesException If even one of the keys has multiple\
            values set.
        """
        results = []
        for key in self.iterkeys():
            value = self.get_value(key)
            results.append(value)
        return results

    def itervalues(self):
        """
        Iterates over the values

        Works only if the whole ranges/view has single values.

        If key is a str the values are single objects.
        If key is iterable (list, tuple, set, etc) of str (or None)\
        values are dictionary objects

        This function is safe for value updates but may miss new keys\
        added during iteration.

        :return: yield values
        :raises MultipleValuesException If even one of the keys has multiple\
            values set.
        """
        for key in self.iterkeys():
            yield self.get_value(key)

    def __contains__(self, key):
        """
        Checks if the key is a dictionary key or a range id

        :param key: Dict key or id to check
        :type key: str or int
        :return: True if the str key is one of the dict keys or\
            if the int key is one of the range ids. Otherwise False
        """
        if isinstance(key, str):
            return self.has_key(key)  # @IgnorePep8
        if isinstance(key, int):
            return key in self.has_id(id)
        raise KeyError("Unexpected key type: {}".format(type(key)))

    @abstractmethod
    def has_key(self, key):
        """
        As the Deprecated dict has_keys function

        Note: Int keys to ids are not supported

        :param key: the key
        :type str
        :return:
        """

    def keys(self):
        """
        Returns the keys in the dictionary

        :return: keys in the dict
        """
        return list(self.iterkeys())

    @abstractmethod
    def iterkeys(self):
        """
        Iterates over the dictionary keys
        :return: yield of each key
        """
        pass

    def reset(self, key):
        """
        Sets the value(s)  for a single key back to the default value

        :param key: Existing dict key
        :type key: str
        :param default: Value to be used by reset
        """
        self.set_value(key, self.get_default(key=key))

    @abstractmethod
    def viewkeys(self):
        """
        Get a view of the dictionary keys that updates when the dictionary\
        changes
        """
