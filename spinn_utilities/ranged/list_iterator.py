class ListIterator(object):

    def __init__(self, inner, start=0, stop=None):
        self._next_index = 0
        self._range = 0
        self._inner = inner
        if stop is None:
            self._stop = inner._size
        else:
            self._stop = stop

    def __iter__(self):
        return self

    def next(self):
        if self._next_index >= self._stop:
            raise StopIteration()
        i = self._next_index
        self._next_index += 1
        try:
            if i >= self._inner._ranges[self._range][0]:
                if i < self._inner._ranges[self._range][1]:
                    return self._inner._ranges[self._range][2]
                if i == self._inner._ranges[self._range][1]:
                    self._range += 1
                    return self._inner._ranges[self._range][2]
        except IndexError:
            # Ranges changed
            pass
        self._range = 0
        while i >= self._inner._ranges[self._range][1]:
            self._range += 1
        if i < self._inner._ranges[self._range][1]:
            return self._inner._ranges[self._range][2]
        raise RuntimeError('list modified duration iteration')

