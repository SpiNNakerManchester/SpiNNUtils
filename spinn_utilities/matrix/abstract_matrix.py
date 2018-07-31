from six import add_metaclass

from spinn_utilities.abstract_base import AbstractBase, abstractmethod


@add_metaclass(AbstractBase)
class AbstractMatrix(object):
    """ A rectangular 2D collection of data.
    """
    __slots__ = []

    @abstractmethod
    def get_data(self, x, y):
        """ Get the value at a particular X,Y coordinate.
        """

    @abstractmethod
    def set_data(self, x, y, value):
        """ Set the value at a particular X,Y coordinate.
        """
