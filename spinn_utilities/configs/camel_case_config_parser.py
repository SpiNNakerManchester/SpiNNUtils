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
import os

from collections.abc import Iterable
import configparser
from typing import List, Optional, Union


NONES = ("none", )
TRUES = ('y', 'yes', 't', 'true', 'on', '1')
FALSES = ('n', 'no', 'f', 'false', 'off', '0')

# Type support
_Path = Union[Union[str, bytes, os.PathLike],
    Iterable[Union[str, bytes, os.PathLike]]]


class CamelCaseConfigParser(configparser.RawConfigParser):
    """
    Extends the Parser to allow for differences in case and underscores
    """
    __slots__ = ["_read_files"]

    def optionxform(self, optionstr: str) -> str:
        """
        Transforms the name of an option to lower case and strips
        underscores, so matching is more user-friendly.
        """
        lower = optionstr.lower()
        return lower.replace("_", "")

    def __init__(self) -> None:
        super().__init__()
        self._read_files: List[str] = list()

    def read(self, filenames: _Path,
             encoding: Optional[str] = None):
        """
        Read and parse a filename or a list of filenames.
        """
        new_files = super().read(filenames, encoding)
        self._read_files.extend(new_files)
        return new_files

    @property
    def read_files(self) -> List[str]:
        """
        The configuration files that have been actually read.
        """
        return self._read_files

    def get_str(self, section: str, option: str) -> Optional[str]:
        """
        Get the string value of an option.

        :param section: What section to get the option from.
        :param option: What option to read.
        :return: The option value
        """
        value = self.get(section, option)
        if value.lower() in NONES:
            return None
        return value

    def get_str_list(
            self, section: str, option: str, token: str = ",") -> List[str]:
        """
        Get the string value of an option split into a list.

        :param section: What section to get the option from.
        :param option: What option to read.
        :param token: The token to split the string into a list
        :return: The list (possibly empty) of the option values
        """
        value = self.get(section, option)
        if value.lower() in NONES:
            return []
        if len(value.strip()) == 0:
            return []
        as_list = value.split(token)
        return list(map(lambda x: x.strip(), as_list))

    def get_int(self, section: str, option: str) -> Optional[int]:
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

    def get_float(self, section: str, option: str) -> Optional[float]:
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

    def get_bool(self, section: str, option: str,
                 special_nones: Optional[List[str]]) -> Optional[bool]:
        """
        Get the Boolean value of an option.

        :param str section: What section to get the option from.
        :param str option: What option to read.
        :param special_nones: What special values to except as None
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
        if special_nones and lower in special_nones:
            return None
        raise ValueError(f"invalid truth value {value}")
