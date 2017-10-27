from spinn_utilities.ranged.abstract_list import AbstractList


class DivList(AbstractList):

    def __init__(self, numerator, divisor, key=None):
        """
        Constructor for a ranged list.

        :param size: Fixed length of the list
        :param default: Default value to given to all elements in the list
        :param key: The dict key this list covers.
        This is used only for better Exception messages
        """
        if numerator._size != divisor._size:
            raise Exception("Numerator and Divisor must have the same size")
        AbstractList.__init__(self, size=numerator._size, key=key)
        self._numerator = numerator
        self._divisor = divisor

    def iter_ranges(self):
        """
        Returns a copy ot the list of ranges.

        As this is a copy it will not refelct any updates
        :return:
        """
        numerator_iter = self._numerator.iter_ranges()
        divisor_iter = self._divisor.iter_ranges()
        return self._merge_ranges(numerator_iter, divisor_iter)

    def get_default(self):
        return self._numerator / self._divisor

    def _merge_ranges(self, numerator_iter, divisor_iter):
        numerator = numerator_iter.next()
        divisor = divisor_iter.next()
        while True:
            yield (max(numerator[0], divisor[0]),
                   min(numerator[1], divisor[1]),
                   numerator[2] / divisor[2])
            if numerator[1] < divisor[1]:
                numerator = numerator_iter.next()
            elif numerator[1] > divisor[1]:
                divisor = divisor_iter.next()
            else:
                numerator = numerator_iter.next()
                divisor = divisor_iter.next()

