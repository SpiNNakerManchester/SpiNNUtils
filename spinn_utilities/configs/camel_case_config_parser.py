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

import configparser
import distutils.util as _du  # pylint: disable=import-error, no-name-in-module


class CamelCaseConfigParser(configparser.RawConfigParser):
    __slots__ = ["_none_marker", "_read_files"]

    def optionxform(self, optionstr):
        """ Transforms the name of an option to lower case and strips\
            underscores, so matching is more user-friendly.
        """
        lower = optionstr.lower()
        return lower.replace("_", "")

    def __init__(self, defaults=None, none_marker="None"):
        super().__init__(defaults)
        self._none_marker = none_marker
        self._read_files = list()

    # pylint: disable=arguments-differ
    def read(self, filenames, encoding=None):
        """ Read and parse a filename or a list of filenames.
        """
        new_files = super().read(filenames, encoding)
        self._read_files.extend(new_files)
        return new_files

    @property
    def read_files(self):
        """ The configuration files that have been actually read.
        """
        return self._read_files

    def get_str(self, section, option):
        """ Get the string value of an option.

        :param section: What section to get the option from.
        :type section: str
        :param option: What option to read.
        :type option: str
        :return: The option value
        :rtype: str or None
        """
        value = self.get(section, option)
        if value == self._none_marker:
            return None
        return value

    def get_str_list(self, section, option, token=","):
        """ Get the string value of an option split into a list

        :param str section: What section to get the option from.
        :param str option: What option to read.
        :param token: The token to split the string into a list
        :return: The list (possibly empty) of the option values
        :rtype: list(str)
        """
        value = self.get(section, option)
        if value == self._none_marker:
            return []
        if len(value.strip()) == 0:
            return []
        as_list = value.split(token)
        return list(map(lambda x: x.strip(), as_list))

    def get_int(self, section, option):
        """ Get the integer value of an option.

        :param section: What section to get the option from.
        :type section: str
        :param option: What option to read.
        :type option: str
        :return: The option value
        :rtype: int
        """
        value = self.get(section, option)
        if value == self._none_marker:
            return None
        return int(value)

    def get_float(self, section, option):
        """ Get the float value of an option.

        :param section: What section to get the option from.
        :type section: str
        :param option: What option to read.
        :type option: str
        :return: The option value.
        :rtype: float
        """
        value = self.get(section, option)
        if value == self._none_marker:
            return None
        return float(value)

    def get_bool(self, section, option):
        """ Get the boolean value of an option.

        :param section: What section to get the option from.
        :type section: str
        :param option: What option to read.
        :type option: str
        :return: The option value.
        :rtype: bool
        """
        value = self.get(section, option)
        if value == self._none_marker:
            return None
        try:
            return bool(_du.strtobool(str(value)))
        except ValueError:
            return bool(value)
