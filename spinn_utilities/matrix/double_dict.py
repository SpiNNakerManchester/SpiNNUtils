from spinn_utilities.matrix.x_view import XView
from spinn_utilities.matrix.y_view import YView
from six import raise_from


class DoubleDict(object):
    __slots__ = [
        "_matrix", "_xtype", "_ytype"]

    def __init__(self, xtype, ytype, matrix):
        self._xtype = xtype
        self._ytype = ytype
        self._matrix = matrix

    def __getitem__(self, key):
        if isinstance(key, self._xtype):
            return XView(x=key, matrix=self._matrix)
        if isinstance(key, self._ytype):
            return YView(y=key, matrix=self._matrix)
        raise KeyError("Key {} has an unexpected type".format(key))

    def __setitem__(self, key, value):
        try:
            if isinstance(key, self._xtype):
                correct = all(isinstance(y, self._ytype) for y in value.keys())
                if not correct:
                    raise ValueError(
                        "All keys in the value must be of type {}".format(
                            self._ytype))
                for y in value.keys():
                    self._matrix.set_data(x=key, y=y, value=value[y])
            elif isinstance(key, self._ytype):
                correct = all(isinstance(x, self._xtype) for x in value.keys())
                if not correct:
                    raise ValueError(
                        "All keys in the value must be of type {}".format(
                            self._xtype))
                for x in value.keys():
                    self._matrix.set_data(x=x, y=key, value=value[x])
            else:
                raise KeyError("Key {} has an unexpected type".format(key))
        except AttributeError as e:
            raise_from(ValueError("Value must of type dict. Or at least "
                                  "implement keys() and __getitem__"), e)
