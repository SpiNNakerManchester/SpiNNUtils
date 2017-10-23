from six import add_metaclass

from spinn_utilities.abstract_base import AbstractBase, abstractproperty, \
    abstractmethod

@add_metaclass(AbstractBase)
class AbstractDict(object):

    @abstractmethod
    def get_value(self, key):
        pass

    #@abstractmethod
    #def iter_values(self, key, fast=True):
    #    pass

    @abstractmethod
    def keys(self):
        pass

    @abstractmethod
    def set_value(self, key, value):
        pass

    @abstractmethod
    def ids(self):
        pass

    @abstractmethod
    def iter_all_values(self, key, fast=True):
        pass

    def items(self):
        results = []
        for key in self.keys():
            value = self.get_value(key)
            results.append((key, value))
        return results

    def iteritems(self):
        for key in self.keys():
            yield (key, self.get_value(key))

    def values(self):
        results = []
        for key in self.keys():
            value = self.get_value(key)
            results.append(value)
        return results

    def itervalues(self):
        for key in self.keys():
            yield self.get_value(key)

    def __contains__(self, key):
        if isinstance(key, str):
            return key in self.keys()
        if isinstance(key, int):
            return key in self.ids
        raise KeyError("Unexpected key type: {}".format(type(key)))

    def has_key(self, key):
        return key in self.keys()

    def iterkeys(self):
        return self.keys().iter()



