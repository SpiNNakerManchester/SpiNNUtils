# Copyright (c) 2017-2018 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import inspect


class overrides(object):
    """ A decorator for indicating that a method overrides another method in\
        a superclass.  This checks that the method does actually exist,\
        copies the doc-string for the method, and enforces that the method\
        overridden is specified, making maintenance easier.
    """

    __slots__ = [
        # The method in the superclass that this method overrides
        "_superclass_method",
        # True if the doc string is to be extended, False to set if not set
        "_extend_doc",
        # Any additional arguments required by the subclass method
        "_additional_arguments",
        # True if the subclass method may have additional defaults
        "_extend_defaults",
        # True if the name check is relaxed
        "_relax_name_check",
        # The name of the thing being overridden for error messages
        "_override_name"
    ]

    def __init__(
            self, super_class_method, extend_doc=True,
            additional_arguments=None, extend_defaults=False):
        """
        :param super_class_method: The method to override in the superclass
        :param bool extend_doc:
            True the method doc string should be appended to the super-method
            doc string, False if the documentation should be set to the
            super-method doc string only if there isn't a doc string already
        :param iterable(str) additional_arguments:
            Additional arguments taken by the subclass method over the
            superclass method, e.g., that are to be injected
        :param bool extend_defaults:
            Whether the subclass may specify extra defaults for the parameters
        """
        self._superclass_method = super_class_method
        self._extend_doc = bool(extend_doc)
        self._extend_defaults = bool(extend_defaults)
        self._relax_name_check = False
        self._override_name = "super class method"
        if additional_arguments is None:
            self._additional_arguments = {}
        else:
            self._additional_arguments = frozenset(additional_arguments)
        if isinstance(super_class_method, property):
            self._superclass_method = super_class_method.fget

    @staticmethod
    def __match_defaults(default_args, super_defaults, extend_ok):
        if default_args is None:
            return super_defaults is None
        elif super_defaults is None:
            return extend_ok
        if extend_ok:
            return len(default_args) >= len(super_defaults)
        return len(default_args) == len(super_defaults)

    def __verify_method_arguments(self, method):
        """ Check that the arguments match. """
        method_args = inspect.getfullargspec(method)
        super_args = inspect.getfullargspec(self._superclass_method)
        all_args = [
            arg for arg in method_args.args
            if arg not in self._additional_arguments]
        default_args = None
        if method_args.defaults is not None:
            default_args = [
                arg for arg in method_args.defaults
                if arg not in self._additional_arguments]
        if len(all_args) != len(super_args.args):
            raise AttributeError(
                "Method has {} arguments but {} has {}"
                " arguments".format(
                    len(method_args.args), self._override_name,
                    len(super_args.args)))
        for arg, super_arg in zip(all_args, super_args.args):
            if arg != super_arg:
                raise AttributeError(
                    "Missing argument {}".format(super_arg))
        if not self.__match_defaults(
                default_args, super_args.defaults, self._extend_defaults):
            raise AttributeError(
                "Default arguments don't match {}".format(
                    self._override_name))

    def __call__(self, method):
        """ Apply the decorator to the given method.
        """

        # Check and fail if this is a property
        if isinstance(method, property):
            raise AttributeError(
                "Please ensure that the {} decorator is the last"
                " decorator before the method declaration".format(
                    self.__class__.__name__))

        # Check that the name matches
        if (not self._relax_name_check and
                method.__name__ != self._superclass_method.__name__):
            raise AttributeError(
                "{} name {} does not match {}. "
                "Ensure {} is the last decorator before the method "
                "declaration".format(
                    self._override_name, self._superclass_method.__name__,
                    method.__name__, self.__class__.__name__))

        # Check that the arguments match (except for __init__ as this might
        # take extra arguments or pass arguments not specified)
        if method.__name__ != "__init__":
            self.__verify_method_arguments(method)

        if (self._superclass_method.__doc__ is not None and
                method.__doc__ is None):
            method.__doc__ = self._superclass_method.__doc__
        elif (self._extend_doc and
                self._superclass_method.__doc__ is not None):
            method.__doc__ = (
                self._superclass_method.__doc__ + method.__doc__)
        return method
