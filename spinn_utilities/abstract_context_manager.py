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


class AbstractContextManager(object, metaclass=AbstractBase):
    """
    Closable class that supports being used as a simple context manager.
    """

    __slots__ = []

    @abstractmethod
    def close(self):
        """
        How to actually close the underlying resources.
        """

    def _context_entered(self):
        """
        Called when the context is entered. The result is ignored.
        """

    def _context_exception_occurred(self, exc_type, exc_val, exc_tb):
        """
        Called when an exception occurs during the `with` context, *after*
        the context has been closed.

        :param type exc_type:
        :param object exc_val:
        :param traceback exc_tb:
        """

    def __enter__(self):
        self._context_entered()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if exc_type:
            self._context_exception_occurred(exc_type, exc_val, exc_tb)
        return False
