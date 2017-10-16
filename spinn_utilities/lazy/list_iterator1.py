class ListIterator1(object):

    def __init__(self, inner):
        self.i = 0
        self._inner = inner

    def next(self):
        if self.i < len(self._inner):
            self.i += 1
            return self._inner[self.i-1]
        else:
            raise StopIteration()
