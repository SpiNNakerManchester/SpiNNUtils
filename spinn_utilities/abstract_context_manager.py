# Copyright (c) 2017 The University of Manchester
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

from typing import Iterable
from .abstract_base import AbstractBase, abstractmethod


class AbstractContextManager(object, metaclass=AbstractBase):
    """ Closeable class that supports being used as a simple context manager.
    """

    __slots__: Iterable[str] = []

    @abstractmethod
    def close(self):
        """ How to actually close the underlying resources.
        """

    def _context_entered(self):
        """ Called when the context is entered. The result is ignored.
        """

    def _context_exception_occurred(self, exc_type, exc_val, exc_tb):
        """ Called when an exception occurs during the `with` context, *after*\
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
