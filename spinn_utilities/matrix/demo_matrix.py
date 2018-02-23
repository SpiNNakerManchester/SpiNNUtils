from spinn_utilities.matrix.abstract_matrix import AbstractMatrix

from collections import defaultdict


class DemoMatrix(AbstractMatrix):
    __slots__ = [
        "data"]

    def __init__(self):
        self.data = defaultdict(dict)

    def get_data(self, x, y):
        return self.data[x][y]

    def set_data(self, x, y, value):
        self.data[x][y] = value
