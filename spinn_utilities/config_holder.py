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

from collections import defaultdict
from configparser import NoOptionError
import logging
import os
from typing import Callable, Collection, Dict, List, Optional, Set, Union

import spinn_utilities.conf_loader as conf_loader
from spinn_utilities.data import UtilsDataView
from spinn_utilities.configs import CamelCaseConfigParser
from spinn_utilities.exceptions import ConfigException
from spinn_utilities.log import (
    FormatAdapter, ConfiguredFilter, ConfiguredFormatter)

# pylint: disable=global-statement
logger = FormatAdapter(logging.getLogger(__file__))

__config: Optional[CamelCaseConfigParser] = None
__default_config_files: List[str] = []
__config_file: Optional[str] = None
__unittest_mode: bool = False


def add_default_cfg(default: str) -> None:
    """
    Adds an extra default configuration file to be read after earlier ones.

    :param str default: Absolute path to the configuration file
    """
    if default not in __default_config_files:
        __default_config_files.append(default)


def clear_cfg_files(unittest_mode: bool) -> None:
    """
    Clears any previous set configurations and configuration files.

    After this method :py:func:`add_default_cfg` and :py:func:`set_cfg_files`
    need to be called.

    :param bool unittest_mode: Flag to put the holder into unit testing mode
    """
    global __config, __config_file, __unittest_mode
    __config = None
    __default_config_files.clear()
    __config_file = None
    __unittest_mode = unittest_mode


def set_cfg_files(config_file: Optional[str], default: str) -> None:
    """
    Adds the configuration files to be loaded.

    :param config_file:
        The base name of the configuration file(s).
        Should not include any path components.
        Use None to not read any file
    :param default:
        Full path to the extra file to get default configurations from.
    """
    global __config_file
    __config_file = config_file
    add_default_cfg(default)


def _pre_load_config() -> CamelCaseConfigParser:
    """
    Loads configurations due to early access to a configuration value.

    :raises ConfigException: Raise if called before setup
    """
    # If you get this error during a unit test, unittest_step was not called
    if not __unittest_mode:
        raise ConfigException(
            "Accessing config values before setup is not supported")
    return load_config()


def logging_parser(config: CamelCaseConfigParser) -> None:
    """
    Create the root logger with the given level.

    Create filters based on logging levels
    """
    try:
        if (has_config_option("Logging", "instantiate") and
                get_config_bool("Logging", "instantiate")):
            level = "INFO"
            if has_config_option("Logging", "default"):
                level = get_config_str("Logging", "default").upper()
            logging.basicConfig(level=level)
        for handler in logging.root.handlers:
            handler.addFilter(
                ConfiguredFilter(config))  # type: ignore[arg-type]
            handler.setFormatter(ConfiguredFormatter(config))
    except NoOptionError:
        pass


def load_config() -> CamelCaseConfigParser:
    """
    Reads in all the configuration files, resetting all values.

    :raises ConfigException: If called before setting defaults
    """
    global __config
    if not __default_config_files:
        raise ConfigException("No default configs set")
    if __config_file:
        __config = conf_loader.load_config(
            filename=__config_file, defaults=__default_config_files)
    else:
        __config = CamelCaseConfigParser()
        for default in __default_config_files:
            __config.read(default)

    logging_parser(__config)
    return __config


def is_config_none(section: str, option: str) -> bool:
    """
    Check if the value of a configuration option would be considered None

    :param section: What section to get the option from.
    :param option: What option to read.
    :return: True if and only if the value would be considered None
    """
    value = get_config_str_or_none(section, option)
    return value is None


def get_config_str(section: str, option: str) -> str:
    """
    Get the string value of a configuration option.

    :param section: What section to get the option from.
    :param option: What option to read.
    :return: The option value
    :raises ConfigException: if the Value would be None
    """
    value = get_config_str_or_none(section, option)
    if value is None:
        raise ConfigException(f"Unexpected None for {section=} {option=}")
    return value


def get_config_str_or_none(section: str, option: str) -> Optional[str]:
    """
    Get the string value of a configuration option.

    :param section: What section to get the option from.
    :param option: What option to read.
    :return: The option value
    :raises ConfigException: if the Value would be None
    """
    if __config is None:
        return _pre_load_config().get_str(section, option)
    else:
        return __config.get_str(section, option)


def get_config_str_list(
        section: str, option: str, token: str = ",") -> List[str]:
    """
    Get the string value of a configuration option split into a list.

    :param section: What section to get the option from.
    :param option: What option to read.
    :param token: The token to split the string into a list
    :return: The list (possibly empty) of the option values
    """
    if __config is None:
        return _pre_load_config().get_str_list(section, option, token)
    else:
        return __config.get_str_list(section, option, token)


def get_config_int(section: str, option: str) -> int:
    """
    Get the integer value of a configuration option.

    :param section: What section to get the option from.
    :param option: What option to read.
    :return: The option value
    :raises ConfigException: if the Value would be None
    """
    value = get_config_int_or_none(section, option)
    if value is None:
        raise ConfigException(f"Unexpected None for {section=} {option=}")
    return value


def get_config_int_or_none(section: str, option: str) -> Optional[int]:
    """
    Get the integer value of a configuration option.

    :param section: What section to get the option from.
    :param option: What option to read.
    :return: The option value
    :raises ConfigException: if the Value would be None
    """
    if __config is None:
        return _pre_load_config().get_int(section, option)
    else:
        return __config.get_int(section, option)


def get_config_float(section: str, option: str) -> float:
    """
    Get the float value of a configuration option.

    :param section: What section to get the option from.
    :param option: What option to read.
    :return: The option value.
    :raises ConfigException: if the Value would be None
    """
    value = get_config_float_or_none(section, option)
    if value is None:
        raise ConfigException(f"Unexpected None for {section=} {option=}")
    return value


def get_config_float_or_none(section: str, option: str) -> Optional[float]:
    """
    Get the float value of a configuration option.

    :param section: What section to get the option from.
    :param option: What option to read.
    :return: The option value.
    """
    if __config is None:
        return _pre_load_config().get_float(section, option)
    else:
        return __config.get_float(section, option)


def get_config_bool(section: str, option: str) -> bool:
    """
    Get the Boolean value of a configuration option.

    :param section: What section to get the option from.
    :param option: What option to read.
    :return: The option value.
    :raises ConfigException: if the Value would be None
    """
    value = get_config_bool_or_none(section, option)
    if value is None:
        raise ConfigException(f"Unexpected None for {section=} {option=}")
    return value


def get_config_bool_or_none(section: str, option: str,
                            special_nones: Optional[List[str]] = None
                            ) -> Optional[bool]:
    """
    Get the Boolean value of a configuration option.

    :param section: What section to get the option from.
    :param option: What option to read.
    :param special_nones: What special values to except as None
    :return: The option value.
    :raises ConfigException: if the Value would be None
    """
    if __config is None:
        return _pre_load_config().get_bool(section, option, special_nones)
    else:
        return __config.get_bool(section, option, special_nones)


def _check_section_exists(section: str) -> None:
    """
    Checks a section exists creating it if needed and in an unittest.

    :param section:
    :raises ConfigException: If no in an unittest
    """
    if not __unittest_mode:
        raise ConfigException(
            "check_section_exists is only allowed in unittests")
    if __config is None:
        _pre_load_config()
    assert __config is not None
    if not __config.has_section(section):
        __config.add_section(section)


def set_config(section: str, option: str, value: Optional[str]) -> None:
    """
    Sets the value of a configuration option.

    This method should only be called by the simulator or by unit tests.

    :param section: What section to set the option in.
    :param option: What option to set.
    :param value: Value to set option to
    :raises ConfigException: If called unexpectedly
    """
    if __config is None:
        _pre_load_config().set(section, option, value)
    else:
        __config.set(section, option, value)


def has_config_option(section: str, option: str) -> bool:
    """
    Check if the section has this configuration option.

    :param section: What section to check
    :param option: What option to check.
    :return: True if and only if the option is defined. It may be `None`
    """
    if __config is None:
        raise ConfigException("configuration not loaded")
    else:
        return __config.has_option(section, option)


def config_options(section: str) -> List[str]:
    """
    Return a list of option names for the given section name.

    :param section: What section to list options for.
    """
    if __config is None:
        raise ConfigException("configuration not loaded")
    return __config.options(section)


def _get_parts(
        line: str, lines: List[str], index: int, start: str) -> List[str]:
    while ")" not in line:
        index += 1
        line += lines[index]
    parts = line[line.find("(", line.find(start)) + 1:
                 line.find(")")].split(",")
    return parts


# Tried to give method a more exact type but expects method to handle both!
# Union[Callable[[str, str], Any],
# Callable[[str, str, Optional[List[str]]], Any]]
def _check_lines(py_path: str, line: str, lines: List[str], index: int,
                 method: Callable, used_cfgs: Dict[str, Set[str]], start: str,
                 special_nones: Optional[List[str]] = None) -> None:
    """
    Support for `_check_python_file`. Gets section and option name.

    :param line: Line with get_config call
    :param lines: All lines in the file
    :param index: index of line with `get_config` call
    :param method: Method to call to check cfg
    :param used_cfgs:
        Dict of used cfg options to be added to
    :param special_nones: What special values to except as None
    :raises ConfigException: If an unexpected or uncovered `get_config` found
    """
    parts = _get_parts(line, lines, index, start)
    section = parts[0].strip().replace("'", "").replace('"', '')
    for i in range(1, len(parts)):
        try:
            option = parts[i].strip()
        except IndexError as original:
            raise ConfigException(
                f"failed in line:{index} of file: {py_path} with {line}") \
                from original
        if option[0] == "'":
            option = option.replace("'", "")
        elif option[0] == '"':
            option = option.replace('"', '')
        else:
            print(line)
            return
        try:
            if special_nones:
                method(section, option, special_nones)
            else:
                method(section, option)
        except Exception as original:
            raise ConfigException(
                f"failed in line:{index} of file: {py_path} with "
                f"section:{section} option:{option}") from original
        used_cfgs[section].add(option)


def _check_get_report_path(
        py_path: str, line: str, lines: List[str], index: int,
        used_cfgs: Dict[str, Set[str]], start: str) -> None:
    """
    Support for `_check_python_file`. Gets section and option name.

    :param line: Line with get_config call
    :param lines: All lines in the file
    :param index: index of line with `get_config` call
    :param method: Method to call to check cfg
    :param used_cfgs:
        Dict of used cfg options to be added to
    :param special_nones: What special values to except as None
    :raises ConfigException: If an unexpected or uncovered `get_config` found
    """
    # Do not check this file
    if py_path.endswith('config_holder.py'):
        return

    parts = _get_parts(line, lines, index, start)
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
            raise ConfigException(f"unexpected {parts=}")

    if option == "option":
        return

    option = option.replace("'", "").replace('"', '')
    section = section.replace("'", "").replace('"', '')
    get_report_path(option, section)
    used_cfgs[section].add(option)


def _check_python_file(py_path: str, used_cfgs: Dict[str, Set[str]],
                       special_nones: Optional[List[str]] = None) -> None:
    """
    A testing function to check that all the `get_config` calls work.

    :param py_path: path to file to be checked
    :param used_cfgs: dict of cfg options found
    :param special_nones: What special values to except as None
    :raises ConfigException: If an unexpected or uncovered `get_config` found
    """
    with open(py_path, 'r', encoding="utf-8") as py_file:
        lines = list(py_file)
        for index, line in enumerate(lines):
            if ("skip_if_cfg" in line):
                _check_lines(py_path, line, lines, index,
                             get_config_bool_or_none, used_cfgs, "skip_if_cfg",
                             special_nones)
            if ("configuration.get" in line):
                _check_lines(py_path, line, lines, index,
                             get_config_bool_or_none, used_cfgs,
                             "configuration.get")
            if ("get_report_path(" in line):
                _check_get_report_path(py_path, line, lines, index, used_cfgs,
                                       "get_report_path(")
            if "get_config" not in line:
                continue
            if (("get_config_bool(" in line) or
                    ("get_config_bool_or_none(" in line)):
                _check_lines(py_path, line, lines, index,
                             get_config_bool_or_none, used_cfgs,
                             "get_config_bool", special_nones)
            if (("get_config_float(" in line) or
                    ("get_config_float_or_none(" in line)):
                _check_lines(py_path, line, lines, index,
                             get_config_float_or_none, used_cfgs, "get_config")
            if (("get_config_int(" in line) or
                    ("get_config_int_or_none(" in line)):
                _check_lines(py_path, line, lines, index,
                             get_config_int_or_none, used_cfgs, "get_config")
            if (("get_config_str(" in line) or
                    ("get_config_str_or_none(" in line)):
                _check_lines(py_path, line, lines, index,
                             get_config_str_or_none, used_cfgs, "get_config")
            if "get_config_str_list(" in line:
                _check_lines(py_path, line, lines, index,
                             get_config_str_list, used_cfgs, "get_config")


def _find_double_defaults(repeaters: Optional[Collection[str]] = ()) -> None:
    """
    Testing function to identify any configuration options in multiple default
    files.

    :param repeaters: List of options that are expected to be repeated.
    :raises ConfigException:
        If two defaults configuration files set the same value
    """
    config1 = CamelCaseConfigParser()
    for default in __default_config_files[:-1]:
        config1.read(default)
    config2 = CamelCaseConfigParser()
    config2.read(__default_config_files[-1])
    if repeaters is None:
        repeaters = []
    else:
        repeaters = frozenset(map(config2.optionxform, repeaters))
    for section in config2.sections():
        for option in config2.options(section):
            if config1.has_option(section, option):
                if option not in repeaters:
                    raise ConfigException(
                        f"cfg:{__default_config_files[-1]} "
                        f"repeats [{section}]{option}")


def _check_cfg_file(config1: CamelCaseConfigParser, cfg_path: str) -> None:
    """
    Support method for :py:func:`check_cfgs`.

    :param config1:
    :param cfg_path:
    :raises ConfigException: If an unexpected option is found
    """
    config2 = CamelCaseConfigParser()
    config2.read(cfg_path)
    for section in config2.sections():
        if not config1.has_section(section):
            raise ConfigException(
                f"cfg:{cfg_path} has unexpected section [{section}]")
        for option in config2.options(section):
            if not config1.has_option(section, option):
                raise ConfigException(
                    f"cfg:{cfg_path} "
                    f"has unexpected options [{section}]{option}")


def _check_cfgs(path: str) -> None:
    """
    A testing function check local configuration files against the defaults.

    It only checks that the option exists in a default.
    It does not check if the option is used or if the value is the expected
    type.

    :param str path: Absolute path to the parent directory to search
    :raises ConfigException: If an unexpected option is found
    """
    config1 = CamelCaseConfigParser()
    for default in __default_config_files:
        config1.read(default)
    directory = os.path.dirname(path)
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(".cfg"):
                cfg_path = os.path.join(root, file_name)
                if cfg_path in __default_config_files:
                    continue
                print(cfg_path)
                _check_cfg_file(config1, cfg_path)


def run_config_checks(directories: Union[str, Collection[str]], *,
                      exceptions: Union[str, Collection[str]] = (),
                      repeaters: Optional[Collection[str]] = (),
                      check_all_used: bool = True,
                      special_nones: Optional[List[str]] = None) -> None:
    """
    Master test.

    Checks that all cfg options read have a default value in one of the
    default files.

    Checks that all default options declared in the current repository
    are used in that repository.

    :param module:
    :param exceptions:
    :param repeaters:
    :param bool check_all_used: Toggle for the used test.
    :param special_nones: What special values to except as None
    :raises ConfigException: If an incorrect directory passed in
    """
    if isinstance(directories, str):
        directories = [directories]

    if exceptions is None:
        exceptions = []
    elif isinstance(exceptions, str):
        exceptions = [exceptions]

    _find_double_defaults(repeaters)

    config1 = CamelCaseConfigParser()
    config1.read(__default_config_files)

    used_cfgs: Dict[str, Set[str]] = defaultdict(set)
    for directory in directories:
        if not os.path.isdir(directory):
            raise ConfigException(f"Unable find {directory}")
        for root, _, files in os.walk(directory):
            for file_name in files:
                if file_name in exceptions:
                    pass
                elif file_name.endswith(".cfg"):
                    cfg_path = os.path.join(root, file_name)
                    if cfg_path in __default_config_files:
                        continue
                    print(cfg_path)
                    _check_cfg_file(config1, cfg_path)
                elif file_name.endswith(".py"):
                    py_path = os.path.join(root, file_name)
                    _check_python_file(py_path, used_cfgs, special_nones)

    if not check_all_used:
        return

    config2 = CamelCaseConfigParser()
    config2.read(__default_config_files[-1])
    for section in config2:
        if section not in used_cfgs:
            if section == config1.default_section:
                continue
            raise ConfigException(f"cfg {section=} was never used")
        found_options = used_cfgs[section]
        found_options = set(map(config2.optionxform, found_options))
        for option in config2.options(section):
            if option not in found_options:
                raise ConfigException(
                    f"cfg {section=} {option=} was never used")


def get_report_path(
        option: str, section: str = "Reports", n_run: Optional[int] = None,
        is_dir: bool = False) -> str:
    """
    Gets and fixes the path for this option

    If the cfg path is relative it will be joined with the run_dir_path.

    Creates the path's directory if it does not exist.

    (n_run) will be replaced with the current/ or provided run number

    Later updates may replace other bracketed expressions as needed
    so avoid using brackets in file names

    :param option: cfg option name
    :param section: cfg section. Needed if not Reports
    :param n_run: If provided will be used instead of the current run number
    :return: An unchecked absolute path to the file or directory
    """
    path = get_config_str(section, option)

    if n_run is not None and n_run > 1:
        if "(n_run)" not in path:
            logger.warning(
                f"cfg option {option} does not have a (n_run) so "
                f"files from different runs may be overwritten")
    if "(n_run)" in path:
        if n_run is None:
            n_run = UtilsDataView.get_run_number()
        path = path.replace("(n_run)", str(n_run))

    if "(reset_str)" in path:
        reset_str = UtilsDataView.get_reset_str()
        path = path.replace("(reset_str)", str(reset_str))

    if "\\" in path:
        path = path.replace("\\", os.sep)

    if not os.path.isabs(path):
        path = os.path.join(UtilsDataView.get_run_dir_path(), path)

    if is_dir:
        os.makedirs(path, exist_ok=True)
    else:
        folder, _ = os.path.split(path)
        os.makedirs(folder, exist_ok=True)

    return path
