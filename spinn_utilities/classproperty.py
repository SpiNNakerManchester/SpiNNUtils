# Copyright (c) 2018 The University of Manchester
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

from typing import Any, Callable, Optional, Type


class _ClassPropertyDescriptor(object):
    """
    A class to handle the management of class properties.
    """

    def __init__(self, fget: Callable) -> None:
        """
        :param fget: Method being wrapped
        """
        self.fget = fget

    def __get__(
            self, obj: Optional[Any], klass: Optional[Type] = None) -> Any:
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()


def classproperty(func: Callable) -> _ClassPropertyDescriptor:
    """
    Defines a property at the class-level.

    Usage::

        class C(object):
            _my_property = "Value"

            @classproperty
            def my_property(cls):
                return cls._my_property
    """
    if not isinstance(func, (classmethod, staticmethod)):
        # mypy claims expression has type "classmethod ...
        func = classmethod(func)  # type: ignore[assignment]

    return _ClassPropertyDescriptor(func)
