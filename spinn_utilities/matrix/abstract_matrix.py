from six import add_metaclass

from spinn_utilities.abstract_base import AbstractBase, abstractmethod


@add_metaclass(AbstractBase)
class AbstractMatrix(object):

    @abstractmethod
    def get_data(self, x, y):
        pass

    @abstractmethod
    def set_data(self, x, y, value):
        pass
