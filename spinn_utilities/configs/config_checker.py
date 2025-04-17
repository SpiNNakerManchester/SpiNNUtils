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
from typing import Callable, Collection, Dict, List, Optional, Set

from spinn_utilities.config_holder import get_default_cfgs, get_config_bool_or_none
from spinn_utilities.configs.camel_case_config_parser import (
    CamelCaseConfigParser, TypedConfigParser)
from spinn_utilities.exceptions import ConfigException


class ConfigChecker(object):

    #__slots__ = ["configs", "directories"]

    def __init__(self, directories: Collection[str]) -> None:
        # SpiNNGym needs check_all_used
        self.configs = TypedConfigParser()
        self.default_cfgs = get_default_cfgs()
        for default_cfg in self.default_cfgs:
            self.configs.read(default_cfg)
        self.directories = directories
        self.file_path = ""
        self.list: List[str] = []
        self.used_cfgs: Dict[str, Set[str]] = defaultdict(set)

    def check(self, local_defaults: bool = True):
        if local_defaults:
            self._find_double_defaults()
        self._read_files()
        if local_defaults:
            self._check_all_used()

    def check_defaults(self) -> None:
        """
        Testing function to identify any configuration options in multiple default
        files.

        :raises ConfigException:
            If two defaults configuration files set the same value
        """
        config1 = CamelCaseConfigParser()
        for default in self.default_cfgs[:-1]:
            config1.read(default)
        config2 = CamelCaseConfigParser()
        config2.read(self.default_cfgs[-1])
        for section in config2.sections():
            for option in config2.options(section):
                if config1.has_option(section, option):
                    raise ConfigException(
                        f"cfg:{self.default_cfgs} "
                        f"repeats [{section}]{option}")

    def _read_files(self):
        for directory in self.directories:
            for root, _, files in os.walk(directory):
                for file_name in files:
                    if file_name.endswith(".cfg"):
                        self.file_path = os.path.join(root, file_name)
                        self._check_cfg_file()
                    elif file_name.endswith(".py"):
                        self.file_path = os.path.join(root, file_name)
                        self._check_python_file()

    def _check_cfg_file(self) -> None:
        """
        Support method for :py:func:`check_cfgs`.

        :param cfg_path:
        :raises ConfigException: If an unexpected option is found
        """
        if self.file_path in self.default_cfgs:
            return

        config2 = TypedConfigParser()
        config2.read(self.file_path)
        for section in config2.sections():
            if not self.configs.has_section(section):
                raise ConfigException(
                    f"cfg:{self.file_path} has unexpected section [{section}]")
            for option in config2.options(section):
                if not self.configs.has_option(section, option):
                    raise ConfigException(
                        f"cfg:{self.file_path} "
                        f"has unexpected options [{section}]{option}")

    def _check_python_file(self) -> None:
        """
        A testing function to check that all the `get_config` calls work.

        :param py_path: path to file to be checked
        :raises ConfigException: If an unexpected or uncovered `get_config` found
        """
        with open(self.file_path, 'r', encoding="utf-8") as py_file:
            self.lines = list(py_file)
            for index, line in enumerate(self.lines):
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
            line += self.lines[index]
        parts = line[line.find("(", line.find(start)) + 1:
                     line.find(")")].split(",")
        return parts

    def _check_lines(self, parts) -> None:
        section = parts[0].strip().replace("'", "").replace('"', '')
        for i in range(1, len(parts)):
            option = parts[i].strip()
            if option[0] == "'":
                option = option.replace("'", "")
            elif option[0] == '"':
                option = option.replace('"', '')
            else:
                #print(parts)
                return

            if not self.configs.has_option(section, option):
                raise ConfigException(
                    f"{self.file_path} has unexpected {section=} {option=}")

            self.used_cfgs[section].add(option)

    def _check_get_report_path(self, parts) -> None:
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
                if self.file_path.endswith("config_holder.py"):
                    return
                raise ConfigException(
                    f"in {self.file_path} unexpected {parts=}")

        if option == "option":
            return

        option = option.replace("'", "").replace('"', '')
        section = section.replace("'", "").replace('"', '')

        if not self.configs.has_option(section, option):
            if self.file_path.endswith("config_checker.py"):
                return
            raise ConfigException(
                f"{self.file_path} has unexpected {section=} {option=}")

        self.used_cfgs[section].add(option)

    def _check_all_used(self):
        current_config = TypedConfigParser()
        current_config.read(self.default_cfgs[-1])
        for section in current_config:
            if section not in self.used_cfgs:
                if section == "DEFAULT":
                    continue
                raise ConfigException(
                    f"in {self.default_cfgs[-1]} {section=} was never used")
            for option in current_config.options(section):
                if option not in self.used_cfgs[section]:
                    raise ConfigException(
                        f"in {self.default_cfgs[-1]} cfg {section=} {option=} "
                        f"was never used")
