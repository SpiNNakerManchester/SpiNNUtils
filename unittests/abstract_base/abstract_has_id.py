from six import add_metaclass
from spinn_utilities.abstract_base import AbstractBase, abstractproperty


@add_metaclass(AbstractBase)
class AbstractHasId(object):
    """ Represents an item with a label
    """

    __slots__ = ()

    def has_id(self):
        return True

    @abstractproperty
    def id(self):
        """ The id of the item

        :return: The id
        :rtype: str
        :raise None: Raises no known exceptions
        """
