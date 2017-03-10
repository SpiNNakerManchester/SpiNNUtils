from six import add_metaclass

from spinn_utilities.abstract_base import AbstractBase, abstractproperty, \
    abstractmethod

@add_metaclass(AbstractBase)
class AbstractHasConstraints(object):
    """ Represents an object with constraints
    """

    __slots__ = ()
    @abstractmethod
    def add_constraint(self, constraint):
        """ Add a new constraint to the collection of constraints

        :param constraint: constraint to add
        :type constraint:\
                    :py:class:`pacman.model.constraints.abstract_constraint.AbstractConstraint`
        :return: None
        :rtype: None
        :raise pacman.exceptions.PacmanInvalidParameterException: If the\
                    constraint is not valid
        """

    @abstractproperty
    def constraints(self):
        """ An iterable of constraints

        :return: iterable of constraints
        :rtype: iterable of\
                    :py:class:`pacman.model.constraints.abstract_constraint\
                    .AbstractConstraint`
        :raise None: Raises no known exceptions
        """
