import inspect
from spinn_utilities.overrides import overrides

try:
    # pylint: disable=no-member
    _introspector = inspect.getfullargspec  # @UndefinedVariable
except AttributeError:
    _introspector = inspect.getargspec


class see(overrides):
    """ A decorator for indicating that the documentation of the method\
        is provided by another method with exactly the same arguments.  Note\
        that this has the same effect as overrides in reality, but is provided\
        to show that the method doesn't actually override
    """

    def __init__(
        self, documentation_method, extend_doc=True,
            additional_arguments=None, extend_defaults=False):
        super(see, self).__init__(
            documentation_method, extend_doc=extend_doc,
            additional_arguments=additional_arguments,
            extend_defaults=extend_defaults)

        # Same as overrides, except name doesn't have to match
        self._relax_name_check = True

        # Give the errors a better name
        self._override_name = "documentation method"
