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

from types import FunctionType, MethodType
from typing import Any, Callable, Optional, List, Tuple, TypeVar

#: :meta private:
Method = TypeVar("Method", bound=Callable[..., Any])


#  pylint: disable=invalid-name
class overrides(object):
    """
    A decorator for indicating that a method overrides another method in
    a superclass.  This checks that the method does actually exist,
    copies the doc-string for the method, and enforces that the method
    overridden is specified, making maintenance easier.
    """
    __slots__ = [
        # The method in the superclass that this method overrides
        "_superclass_method",
        # True if the doc string is to be extended, False to set if not set
        "_extend_doc",
    ]

    def __init__(
            self, super_class_method: Callable, *, extend_doc: bool = True):
        """
        :param super_class_method: The method to override in the superclass
        :param bool extend_doc:
            True the method doc string should be appended to the super-method
            doc string, False if the documentation should be set to the
            super-method doc string only if there isn't a doc string already
        """
        if isinstance(super_class_method, property):
            super_class_method = super_class_method.fget
        if not isinstance(super_class_method, (FunctionType, MethodType)):
            raise TypeError("may only decorate method declarations; "
                            f"this is a {type(super_class_method)}")
        self._superclass_method = super_class_method
        self._extend_doc = bool(extend_doc)

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
        if (method.__name__ != self._superclass_method.__name__):
            raise AttributeError(
                f"Name mismatch: {self._superclass_method.__name__} "
                f" !=- {method.__name__}")

        if (self._superclass_method.__doc__ is not None and
                method.__doc__ is None):
            method.__doc__ = self._superclass_method.__doc__
        elif (self._extend_doc and
                self._superclass_method.__doc__ is not None):
            method.__doc__ = (
                self._superclass_method.__doc__ + (method.__doc__ or ""))
        return method
