try:
    from collections.abc import defaultdict
except ImportError:
    from collections import defaultdict
from spinn_utilities.overrides import overrides
from .abstract_matrix import AbstractMatrix


class DemoMatrix(AbstractMatrix):
    __slots__ = [
        "data"]

    def __init__(self):
        self.data = defaultdict(dict)

    @overrides(AbstractMatrix.get_data)
    def get_data(self, x, y):
        return self.data[x][y]

    @overrides(AbstractMatrix.set_data)
    def set_data(self, x, y, value):
        self.data[x][y] = value
