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

from .abstract_base import AbstractBase, abstractmethod
from types import TracebackType
from typing import Optional, Type
from typing_extensions import Literal, Self


class AbstractContextManager(object, metaclass=AbstractBase):
    """
    Closable class that supports being used as a simple context manager.
    """

    __slots__ = ()

    @abstractmethod
    def close(self) -> None:
        """
        How to actually close the underlying resources.
        """

    def _context_entered(self) -> None:
        """
        Called when the context is entered. The result is ignored.

        :meta public:
        """

    def _context_exception_occurred(
            self, exc_val: Exception, exc_tb: TracebackType):
        """
        Called when an exception occurs during the `with` context, *after*
        the context has been closed.

        :param Exception exc_val:
        :param ~types.TracebackType exc_tb:
        :meta public:
        """

    def __enter__(self) -> Self:
        self._context_entered()
        return self

    def __exit__(self, exc_type: Optional[Type], exc_val: Exception,
                 exc_tb: TracebackType) -> Literal[False]:
        self.close()
        if exc_type:
            self._context_exception_occurred(exc_type, exc_val, exc_tb)
        return False
