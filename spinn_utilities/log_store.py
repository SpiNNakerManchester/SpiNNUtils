# Copyright (c) 2022 The University of Manchester
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

from .abstract_base import abstractmethod


class LogStore(object):

    @abstractmethod
    def store_log(self, level, message):
        """
        Writes the log message or later retreival
        :param int level:
        :param str message:
        """

    @abstractmethod
    def retreive_log_messages(self, min_level=0):
        """
        Retrieves all log messages at or above the min_level

        :param int min_level:
        :rtype: list(tuple(int, str))
        """

    @abstractmethod
    def get_location(self):
        """
        Retrieves the location of the log store

        :rtype: str
        """
