class AbstractDict(object):

    # self.get_value(key)

    # self.keys()_

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
        return key in self._value_lists

