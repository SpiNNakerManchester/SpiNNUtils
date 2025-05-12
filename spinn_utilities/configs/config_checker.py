# Copyright (c) 2025 The University of Manchester
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

from collections import defaultdict
import os
from typing import Collection, Dict, List, Set

from spinn_utilities.config_holder import get_default_cfgs
from spinn_utilities.configs.camel_case_config_parser import (
    CamelCaseConfigParser, TypedConfigParser)
from spinn_utilities.exceptions import ConfigException


class ConfigChecker(object):
    """
    Checks the py and cfg files after the defaults have been set,
    """

    __slots__ = ["_configs",
                 "_default_cfgs",
                 "_directories",
                 "_file_path",
                 "_lines",
                 "_used_cfgs"]

    def __init__(self, directories: Collection[str]) -> None:
        # SpiNNGym needs check_all_used
        self._configs = TypedConfigParser()
        self._default_cfgs = get_default_cfgs()
        for default_cfg in self._default_cfgs:
            self._configs.read(default_cfg)
        self._directories = directories
        self._file_path = ""
        self._lines: List[str] = []
        self._used_cfgs: Dict[str, Set[str]] = defaultdict(set)

    def check(self, local_defaults: bool = True) -> None:
        """
        Runs the checks of py and cfg files

        :param local_defaults:
        :return:
        """
        if local_defaults:
            self._check_defaults()
        self._read_files()
        if local_defaults:
            self._check_all_used()

    def _check_defaults(self) -> None:
        """
        Testing function to identify any configuration options /
        in multiple default files.

        :raises ConfigException:
            If two defaults configuration files set the same value
        """
        config1 = CamelCaseConfigParser()
        for default in self._default_cfgs[:-1]:
            config1.read(default)
        config2 = CamelCaseConfigParser()
        config2.read(self._default_cfgs[-1])
        for section in config2.sections():
            for option in config2.options(section):
                if config1.has_option(section, option):
                    raise ConfigException(
                        f"cfg:{self._default_cfgs} "
                        f"repeats [{section}]{option}")

    def _read_files(self) -> None:
        for directory in self._directories:
            for root, _, files in os.walk(directory):
                for file_name in files:
                    if file_name.endswith(".cfg"):
                        self._file_path = os.path.join(root, file_name)
                        self._check_cfg_file()
                    elif file_name.endswith(".py"):
                        self._file_path = os.path.join(root, file_name)
                        self._check_python_file()

    def _check_cfg_file(self) -> None:
        """
        Support method for :py:func:`check_cfgs`.

        :param cfg_path:
        :raises ConfigException: If an unexpected option is found
        """
        if self._file_path in self._default_cfgs:
            return

        config2 = TypedConfigParser()
        config2.read(self._file_path)
        for section in config2.sections():
            if not self._configs.has_section(section):
                raise ConfigException(f"cfg:{self._file_path} has "
                                      f"unexpected section [{section}]")
            for option in config2.options(section):
                if not self._configs.has_option(section, option):
                    raise ConfigException(
                        f"cfg:{self._file_path} "
                        f"has unexpected options [{section}]{option}")

    def _check_python_file(self) -> None:
        """
        A testing function to check that all the `get_config` calls work.

        :param py_path: path to file to be checked
        :raises ConfigException:
            If an unexpected or uncovered `get_config` found
        """
        with open(self._file_path, 'r', encoding="utf-8") as py_file:
            self._lines = list(py_file)
            for index, line in enumerate(self._lines):
                if ("skip_if_cfg" in line):
                    parts = self._get_parts(line, index, "skip_if_cfg")
                    self._check_lines(parts)
                elif ("configuration.get" in line):
                    parts = self._get_parts(line, index, "configuration.get")
                    self._check_lines(parts)
                if ("get_report_path(" in line):
                    parts = self._get_parts(line, index, "get_report")
                    self._check_get_report_path(parts)
                if ("get_timestamp_path(" in line):
                    parts = self._get_parts(line, index, "get_timestamp")
                    self._check_get_report_path(parts)
                if "get_config" not in line:
                    continue
                if (("get_config_bool(" in line) or
                        ("get_config_bool_or_none(" in line) or
                        ("get_config_float(" in line) or
                        ("get_config_float_or_none(" in line) or
                        ("get_config_int(" in line) or
                        ("get_config_int_or_none(" in line) or
                        ("get_config_str(" in line) or
                        ("get_config_str_or_none(" in line) or
                        ("get_config_str_list(" in line)):
                    parts = self._get_parts(line, index, "get_config")
                    self._check_lines(parts)

    def _get_parts(self, line: str, index: int, start: str) -> List[str]:
        while ")" not in line:
            index += 1
            line += self._lines[index]
        parts = line[line.find("(", line.find(start)) + 1:
                     line.find(")")].split(",")
        return parts

    def _check_lines(self, parts: List[str]) -> None:
        section = parts[0].strip().replace("'", "").replace('"', '')
        for i in range(1, len(parts)):
            option = parts[i].strip()
            if option[0] == "'":
                option = option.replace("'", "")
            elif option[0] == '"':
                option = option.replace('"', '')
            else:
                return

            if option.startswith("@"):
                raise ConfigException(
                    f"{self._file_path} has {option=} which starts with @")
            if not self._configs.has_option(section, option):
                raise ConfigException(
                    f"{self._file_path} has unexpected {section=} {option=}")

            self._used_cfgs[section].add(option)

    def _check_get_report_path(self, parts: List[str]) -> None:
        section = "Reports"
        option = "No Option found"
        for part in parts:
            part = part.strip()
            if "=" not in part:
                option = part
            elif part.startswith("option="):
                option = part[7:]
            elif part.startswith("section="):
                section = part[8:]
            elif part.startswith("is_dir="):
                pass
            elif part.startswith("n_run="):
                pass
            else:
                if self._file_path.endswith("config_holder.py"):
                    return
                raise ConfigException(
                    f"in {self._file_path} unexpected {parts=}")

        if option == "option":
            return

        option = option.replace("'", "").replace('"', '')
        section = section.replace("'", "").replace('"', '')

        if not self._configs.has_option(section, option):
            if self._file_path.endswith("config_checker.py"):
                return
            raise ConfigException(
                f"{self._file_path} has unexpected {section=} {option=}")

        self._used_cfgs[section].add(option)

    def _check_all_used(self) -> None:
        current_config = TypedConfigParser()
        current_config.read(self._default_cfgs[-1])
        for section in current_config:
            if section not in self._used_cfgs:
                if section == "DEFAULT":
                    continue
                raise ConfigException(
                    f"in {self._default_cfgs[-1]} {section=} was never used")
            for option in current_config.options(section):
                if option.startswith("@"):
                    continue
                if option not in self._used_cfgs[section]:
                    raise ConfigException(
                        f"in {self._default_cfgs[-1]} cfg "
                        f"{section=} {option=} was never used")
