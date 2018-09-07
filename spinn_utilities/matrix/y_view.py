class YView(object):
    """ A view along a particular y-slice of a 2D matrix.
    """
    __slots__ = [
        "_matrix", "_y"]

    def __init__(self, y, matrix):
        self._y = y
        self._matrix = matrix

    def __getitem__(self, key):
        return self._matrix.get_data(x=key, y=self._y)

    def __setitem__(self, key, value):
        self._matrix.set_data(x=key, y=self._y, value=value)
