from spinn_utilities.matrix.abstract_matrix import AbstractMatrix

from collections import defaultdict
from spinn_utilities.overrides import overrides


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
