from six import add_metaclass

from spinn_utilities.abstract_base import AbstractBase, abstractproperty, \
    abstractmethod

@add_metaclass(AbstractBase)
class AbstractHasLabel(object):
    """ Represents an item with a label
    """

    __slots__ = ()

    @abstractproperty
    def label(self):
        """ The label of the item

        :return: The label
        :rtype: str
        :raise None: Raises no known exceptions
        """

    @abstractmethod
    def set_label(selfself, label):
        """

        :param label:
        :return:
        """