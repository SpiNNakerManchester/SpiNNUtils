from spinn_utilities.ranged.dual_list import DualList


class DivList(DualList):

    def __init__(self, left, right, key=None):
        DualList.__init__(self, left=left, right=right, key=key)

    def get_default(self):
        return self._left / self._right

    def _merge_values(self, left, right):
        return left / right

