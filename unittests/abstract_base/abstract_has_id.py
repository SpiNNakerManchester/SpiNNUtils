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

from spinn_utilities.abstract_base import AbstractBase, abstractproperty


class AbstractHasId(object, metaclass=AbstractBase):
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
