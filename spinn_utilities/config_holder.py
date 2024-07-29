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
from typing import Any, Callable, Collection, Dict, List, Optional, Set, Union
import spinn_utilities.conf_loader as conf_loader
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


def add_default_cfg(default: str):
    """
    Adds an extra default configuration file to be read after earlier ones.

    :param str default: Absolute path to the configuration file
    """
    if default not in __default_config_files:
        __default_config_files.append(default)


def clear_cfg_files(unittest_mode: bool):
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


def set_cfg_files(config_file: str, default: str):
    """
    Adds the configuration files to be loaded.

    :param str config_file:
        The base name of the configuration file(s).
        Should not include any path components.
    :param str default:
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


def logging_parser(config: CamelCaseConfigParser):
    """
    Create the root logger with the given level.

    Create filters based on logging levels

    .. note::
        You do not normally need to call this function; it is used
        automatically to parse Logging configuration sections.
    """
    try:
        if get_config_bool("Logging", "instantiate"):
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
            filename=__config_file, defaults=__default_config_files,
            config_parsers=[("Logging", logging_parser)])
    else:
        __config = CamelCaseConfigParser()
        for default in __default_config_files:
            __config.read(default)
    return __config


def is_config_none(section, option) -> bool:
    """
    Check if the value of a configuration option would be considered None

    :param str section: What section to get the option from.
    :param str option: What option to read.
    :return: True if and only if the value would be considered None
    :rtype: bool
    """
    value = get_config_str_or_none(section, option)
    return value is None


def get_config_str(section, option) -> str:
    """
    Get the string value of a configuration option.

    :param str section: What section to get the option from.
    :param str option: What option to read.
    :return: The option value
    :rtype: str
    :raises ConfigException: if the Value would be None
    """
    value = get_config_str_or_none(section, option)
    if value is None:
        raise ConfigException(f"Unexpected None for {section=} {option=}")
    return value


def get_config_str_or_none(section, option) -> Optional[str]:
    """
    Get the string value of a configuration option.

    :param str section: What section to get the option from.
    :param str option: What option to read.
    :return: The option value
    :rtype: str or None
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

    :param str section: What section to get the option from.
    :param str option: What option to read.
    :param token: The token to split the string into a list
    :return: The list (possibly empty) of the option values
    :rtype: list(str)
    """
    if __config is None:
        return _pre_load_config().get_str_list(section, option, token)
    else:
        return __config.get_str_list(section, option, token)


def get_config_int(section: str, option: str) -> int:
    """
    Get the integer value of a configuration option.

    :param str section: What section to get the option from.
    :param str option: What option to read.
    :return: The option value
    :rtype: int
    :raises ConfigException: if the Value would be None
    """
    value = get_config_int_or_none(section, option)
    if value is None:
        raise ConfigException(f"Unexpected None for {section=} {option=}")
    return value


def get_config_int_or_none(section, option) -> Optional[int]:
    """
    Get the integer value of a configuration option.

    :param str section: What section to get the option from.
    :param str option: What option to read.
    :return: The option value
    :rtype: int or None
    :raises ConfigException: if the Value would be None
    """
    if __config is None:
        return _pre_load_config().get_int(section, option)
    else:
        return __config.get_int(section, option)


def get_config_float(section: str, option: str) -> float:
    """
    Get the float value of a configuration option.

    :param str section: What section to get the option from.
    :param str option: What option to read.
    :return: The option value.
    :rtype: float
    :raises ConfigException: if the Value would be None
    """
    value = get_config_float_or_none(section, option)
    if value is None:
        raise ConfigException(f"Unexpected None for {section=} {option=}")
    return value


def get_config_float_or_none(section, option) -> Optional[float]:
    """
    Get the float value of a configuration option.

    :param str section: What section to get the option from.
    :param str option: What option to read.
    :return: The option value.
    :rtype: float or None
    """
    if __config is None:
        return _pre_load_config().get_float(section, option)
    else:
        return __config.get_float(section, option)


def get_config_bool(section: str, option: str) -> bool:
    """
    Get the Boolean value of a configuration option.

    :param str section: What section to get the option from.
    :param str option: What option to read.
    :return: The option value.
    :rtype: bool
    :raises ConfigException: if the Value would be None
    """
    value = get_config_bool_or_none(section, option)
    if value is None:
        raise ConfigException(f"Unexpected None for {section=} {option=}")
    return value


def get_config_bool_or_none(section, option) -> Optional[bool]:
    """
    Get the Boolean value of a configuration option.

    :param str section: What section to get the option from.
    :param str option: What option to read.
    :return: The option value.
    :rtype: bool
    :raises ConfigException: if the Value would be None
    """
    if __config is None:
        return _pre_load_config().get_bool(section, option)
    else:
        return __config.get_bool(section, option)


def set_config(section: str, option: str, value: Optional[str]):
    """
    Sets the value of a configuration option.

    This method should only be called by the simulator or by unit tests.

    :param str section: What section to set the option in.
    :param str option: What option to set.
    :param object value: Value to set option to
    :raises ConfigException: If called unexpectedly
    """
    if __config is None:
        _pre_load_config().set(section, option, value)
    else:
        __config.set(section, option, value)


def has_config_option(section: str, option: str) -> bool:
    """
    Check if the section has this configuration option.

    :param str section: What section to check
    :param str option: What option to check.
    :rtype: bool
    :return: True if and only if the option is defined. It may be `None`
    """
    if __config is None:
        raise ConfigException("configuration not loaded")
    else:
        return __config.has_option(section, option)


def config_options(section: str) -> List[str]:
    """
    Return a list of option names for the given section name.

    :param str section: What section to list options for.
    """
    if __config is None:
        raise ConfigException("configuration not loaded")
    return __config.options(section)


def _check_lines(py_path: str, line: str, lines: List[str], index: int,
                 method: Callable[[str, str], Any],
                 used_cfgs: Dict[str, Set[str]], start):
    """
    Support for `_check_python_file`. Gets section and option name.

    :param str line: Line with get_config call
    :param list(str) lines: All lines in the file
    :param int index: index of line with `get_config` call
    :param method: Method to call to check cfg
    :param dict(str), set(str) used_cfgs:
        Dict of used cfg options to be added to
    :raises ConfigException: If an unexpected or uncovered `get_config` found
    """
    while ")" not in line:
        index += 1
        line += lines[index]
    parts = line[line.find("(", line.find(start)) + 1:
                 line.find(")")].split(",")
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
            method(section, option)
        except Exception as original:
            raise ConfigException(
                f"failed in line:{index} of file: {py_path} with "
                f"section:{section} option:{option}") from original
        used_cfgs[section].add(option)


def _check_python_file(py_path: str, used_cfgs: Dict[str, Set[str]]):
    """
    A testing function to check that all the `get_config` calls work.

    :param str py_path: path to file to be checked
    :param used_cfgs: dict of cfg options found
    :raises ConfigException: If an unexpected or uncovered `get_config` found
    """
    with open(py_path, 'r', encoding="utf-8") as py_file:
        lines = list(py_file)
        for index, line in enumerate(lines):
            if ("skip_if_cfg" in line):
                _check_lines(py_path, line, lines, index,
                             get_config_bool_or_none, used_cfgs, "skip_if_cfg")
            if ("configuration.get" in line):
                _check_lines(py_path, line, lines, index,
                             get_config_bool_or_none, used_cfgs,
                             "configuration.get")
            if "get_config" not in line:
                continue
            if (("get_config_bool(" in line) or
                    ("get_config_bool_or_none(" in line)):
                _check_lines(py_path, line, lines, index,
                             get_config_bool_or_none, used_cfgs, "get_config")
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


def _find_double_defaults(repeaters: Optional[Collection[str]] = ()):
    """
    Testing function to identify any configuration options in multiple default
    files.

    :param repeaters: List of options that are expected to be repeated.
    :type repeaters: list(str)
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


def _check_cfg_file(config1: CamelCaseConfigParser, cfg_path: str):
    """
    Support method for :py:func:`check_cfgs`.

    :param CamelCaseConfigParser config1:
    :param str cfg_path:
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


def _check_cfgs(path: str):
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
                      check_all_used: bool = True):
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
                    _check_python_file(py_path, used_cfgs)

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
