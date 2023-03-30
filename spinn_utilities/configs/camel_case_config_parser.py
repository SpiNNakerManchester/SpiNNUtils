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

import configparser


NONES = ("none", )
TRUES = ('y', 'yes', 't', 'true', 'on', '1')
FALSES = ('n', 'no', 'f', 'false', 'off', '0')


class CamelCaseConfigParser(configparser.RawConfigParser):
    __slots__ = ["_read_files"]

    def optionxform(self, optionstr):
        """
        Transforms the name of an option to lower case and strips
        underscores, so matching is more user-friendly.
        """
        lower = optionstr.lower()
        return lower.replace("_", "")

    def __init__(self, defaults=None):
        super().__init__(defaults)
        self._read_files = list()

    def read(self, filenames, encoding=None):
        """
        Read and parse a filename or a list of filenames.
        """
        new_files = super().read(filenames, encoding)
        self._read_files.extend(new_files)
        return new_files

    @property
    def read_files(self):
        """
        The configuration files that have been actually read.
        """
        return self._read_files

    def get_str(self, section, option):
        """
        Get the string value of an option.

        :param str section: What section to get the option from.
        :param str option: What option to read.
        :return: The option value
        :rtype: str or None
        """
        value = self.get(section, option)
        if value.lower() in NONES:
            return None
        return value

    def get_str_list(self, section, option, token=","):
        """
        Get the string value of an option split into a list.

        :param str section: What section to get the option from.
        :param str option: What option to read.
        :param token: The token to split the string into a list
        :return: The list (possibly empty) of the option values
        :rtype: list(str)
        """
        value = self.get(section, option)
        if value.lower() in NONES:
            return []
        if len(value.strip()) == 0:
            return []
        as_list = value.split(token)
        return list(map(lambda x: x.strip(), as_list))

    def get_int(self, section, option):
        """
        Get the integer value of an option.

        :param str section: What section to get the option from.
        :param str option: What option to read.
        :return: The option value
        :rtype: int
        """
        value = self.get(section, option)
        if str(value).lower() in NONES:
            return None
        return int(value)

    def get_float(self, section, option):
        """
        Get the float value of an option.

        :param str section: What section to get the option from.
        :param str option: What option to read.
        :return: The option value.
        :rtype: float
        """
        value = self.get(section, option)
        if str(value).lower() in NONES:
            return None
        return float(value)

    def get_bool(self, section, option):
        """
        Get the boolean value of an option.

        :param str section: What section to get the option from.
        :param str option: What option to read.
        :return: The option value.
        :rtype: bool
        """
        value = self.get(section, option)
        lower = str(value).lower()
        if lower in TRUES:
            return True
        if lower in FALSES:
            return False
        if lower in NONES:
            return None
        raise ValueError(f"invalid truth value {value}")
