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

import distutils.util as _du  # pylint: disable=import-error, no-name-in-module
from six.moves import configparser


# pylint: disable=slots-on-old-class
class CamelCaseConfigParser(configparser.RawConfigParser):
    # RawConfigParser is a classobj in Python 2.7, not a type (i.e., it
    # doesn't inherit from object), and so cannot be used with super().
    __slots__ = ["_none_marker", "_read_files"]

    def optionxform(self, optionstr):
        """ Transforms the name of an option to lower case and strips\
            underscores, so matching is more user-friendly.
        """
        lower = optionstr.lower()
        return lower.replace("_", "")

    def __init__(self, defaults=None, none_marker="None"):
        configparser.RawConfigParser.__init__(self, defaults)
        self._none_marker = none_marker
        self._read_files = list()

    # pylint: disable=arguments-differ
    def read(self, filenames, encoding=None):
        """ Read and parse a filename or a list of filenames.
        """
        if encoding is not None:
            # pylint: disable=too-many-function-args
            new_files = configparser.RawConfigParser.read(
                self, filenames, encoding)
        else:
            new_files = configparser.RawConfigParser.read(self, filenames)
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
