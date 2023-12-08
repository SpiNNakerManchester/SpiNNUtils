# Copyright (c) 2017 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inspect
from types import FunctionType, MethodType
from typing import Any, Callable, Iterable, Optional, TypeVar

#: :meta private:
Method = TypeVar("Method", bound=Callable[..., Any])


class overrides(object):
    """
    A decorator for indicating that a method overrides another method in
    a superclass.  This checks that the method does actually exist,
    copies the doc-string for the method, and enforces that the method
    overridden is specified, making maintenance easier.
    """
    # This near constant is changed by unittests to check our code
    __CHECK_TYPES = False

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
        "_override_name",
        # True if this method adds typing info not in the original
        "_adds_typing"
    ]

    def __init__(
            self, super_class_method, *, extend_doc: bool = True,
            additional_arguments: Optional[Iterable[str]] = None,
            extend_defaults: bool = False, adds_typing: bool = False,):
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
        :param adds_typing:
            Allows more typing (of non additional) than in the subclass.
            Should only be used for builtin super classes
        """
        if isinstance(super_class_method, property):
            super_class_method = super_class_method.fget
        if not isinstance(super_class_method, (FunctionType, MethodType)):
            raise TypeError("may only decorate method declarations; "
                            f"this is a {type(super_class_method)}")
        self._superclass_method = super_class_method
        self._extend_doc = bool(extend_doc)
        self._extend_defaults = bool(extend_defaults)
        self._relax_name_check = False
        self._override_name = "super class method"
        if additional_arguments is not None:
            self._additional_arguments = frozenset(additional_arguments)
        else:
            self._additional_arguments = frozenset()
        self._adds_typing = adds_typing

    @staticmethod
    def __match_defaults(default_args, super_defaults, extend_ok):
        if default_args is None:
            return super_defaults is None
        elif super_defaults is None:
            return extend_ok
        if extend_ok:
            return len(default_args) >= len(super_defaults)
        return len(default_args) == len(super_defaults)

    def _verify_types(self, method_args, super_args, all_args):
        """
        Check that the arguments match.
        """
        if not self.__CHECK_TYPES:
            return
        if "self" in all_args:
            all_args.remove("self")
        elif "cls" in all_args:
            all_args.remove("cls")
        method_types = method_args.annotations
        super_types = super_args.annotations
        for arg in all_args:
            if arg not in super_types and not self._adds_typing:
                raise AttributeError(
                    f"Super Method {self._superclass_method.__name__} "
                    f"has untyped arguments including {arg}")
            if arg not in method_types:
                raise AttributeError(
                    f"Method {self._superclass_method.__name__} "
                    f"has untyped arguments including {arg}")

        if len(all_args) == 0:
            if "return" not in super_types and not self._adds_typing:
                raise AttributeError(
                    f"Super Method {self._superclass_method.__name__} "
                    f"has no arguments so should declare a return type")
        if "return" in super_types:
            if "return" not in method_types:
                raise AttributeError(
                    f"Method {self._superclass_method.__name__} "
                    f"has no return type, while super does")
        else:
            if "return" in method_types and not self._adds_typing:
                raise AttributeError(
                    f"Super Method {self._superclass_method.__name__} "
                    f"has no return type, while this does")

    def __verify_method_arguments(self, method: Method):
        """
        Check that the arguments match.
        """
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
                f"Method has {len(method_args.args)} arguments but "
                f"{self._override_name} has {len(super_args.args)} arguments")
        for arg, super_arg in zip(all_args, super_args.args):
            if arg != super_arg:
                raise AttributeError(f"Missing argument {super_arg}")
        if not self.__match_defaults(
                default_args, super_args.defaults, self._extend_defaults):
            raise AttributeError(
                f"Default arguments don't match {self._override_name}")
        self._verify_types(method_args, super_args, all_args)

    def __call__(self, method: Method) -> Method:
        """
        Apply the decorator to the given method.
        """
        # Check and fail if this is a property
        if isinstance(method, property):
            raise AttributeError(
                f"Please ensure that the {self.__class__.__name__} decorator "
                "is the last decorator before the method declaration")

        # Check that the name matches
        if (not self._relax_name_check and
                method.__name__ != self._superclass_method.__name__):
            raise AttributeError(
                f"{self._override_name} name "
                f"{self._superclass_method.__name__} does not match "
                f"{method.__name__}. Ensure {self.__class__.__name__} is the "
                "last decorator before the method declaration")

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
                self._superclass_method.__doc__ + (method.__doc__ or ""))
        return method

    @classmethod
    def check_types(cls):
        cls.__CHECK_TYPES = True
