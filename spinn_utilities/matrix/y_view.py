class YView(object):

    def __init__(self, y, matrix):
        self._y = y
        self._matrix = matrix

    def __getitem__(self, key):
        return self._matrix.get_data(x=key, y=self._y)

    def __setitem__(self, key, value):
        self._matrix.set_data(x=key, y=self._y, value=value)
