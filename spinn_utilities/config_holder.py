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

import logging
import os
import spinn_utilities.conf_loader as conf_loader
from spinn_utilities.configs import CamelCaseConfigParser
from spinn_utilities.exceptions import ConfigException
from spinn_utilities.log import FormatAdapter

# pylint: disable=global-statement
logger = FormatAdapter(logging.getLogger(__file__))

__config = None
__default_config_files = []
__config_file = None
__unittest_mode = False


def add_default_cfg(default):
    """
    Adds an extra default configuration file to be read after earlier ones.

    :param str default: Absolute path to the configuration file
    """
    if default not in __default_config_files:
        __default_config_files.append(default)


def clear_cfg_files(unittest_mode):
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


def set_cfg_files(config_file, default):
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


def _pre_load_config():
    """
    Loads configurations due to early access to a configuration value.

    :raises ConfigException: Raise if called before setup
    """
    # If you getthis error during a unittest then unittest_step was not called
    if not __unittest_mode:
        raise ConfigException(
            "Accessing config values before setup is not supported")
    load_config()


def load_config():
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


def get_config_str(section, option):
    """
    Get the string value of a configuration option.

    :param str section: What section to get the option from.
    :param str option: What option to read.
    :return: The option value
    :rtype: str or None
    """
    try:
        return __config.get_str(section, option)
    except AttributeError:
        pass
    _pre_load_config()
    return __config.get_str(section, option)


def get_config_str_list(section, option, token=","):
    """
    Get the string value of a configuration option split into a list.

    :param str section: What section to get the option from.
    :param str option: What option to read.
    :param token: The token to split the string into a list
    :return: The list (possibly empty) of the option values
    :rtype: list(str)
    """
    try:
        return __config.get_str_list(section, option, token)
    except AttributeError:
        pass
    _pre_load_config()
    return __config.get_str_list(section, option, token)


def get_config_int(section, option):
    """
    Get the integer value of a configuration option.

    :param str section: What section to get the option from.
    :param str option: What option to read.
    :return: The option value
    :rtype: int
    """
    try:
        return __config.get_int(section, option)
    except AttributeError:
        pass
    _pre_load_config()
    return __config.get_int(section, option)


def get_config_float(section, option):
    """
    Get the float value of a configuration option.

    :param str section: What section to get the option from.
    :param str option: What option to read.
    :return: The option value.
    :rtype: float
    """
    try:
        return __config.get_float(section, option)
    except AttributeError:
        pass
    _pre_load_config()
    return __config.get_float(section, option)


def get_config_bool(section, option):
    """
    Get the boolean value of a configuration option.

    :param str section: What section to get the option from.
    :param str option: What option to read.
    :return: The option value.
    :rtype: bool
    """
    try:
        return __config.get_bool(section, option)
    except AttributeError:
        pass
    _pre_load_config()
    return __config.get_bool(section, option)


def set_config(section, option, value):
    """
    Sets the value of a configuration option.

    This method should only be called by the simulator or by unit tests.

    :param str section: What section to set the option in.
    :param str option: What option to set.
    :param object value: Value to set option to
    :raises ConfigException: If called unexpectedly
    """
    if __config is None:
        if __unittest_mode:
            load_config()
        else:
            # The actual error is that load_config should be called before
            # set_config but this discourages the use outside of unittests
            raise ConfigException(
                "set_config should only be called by unittests "
                "which should have called unittest_setup")
    __config.set(section, option, value)
    # Intentionally no try here to force tests that set to
    # load_default_configs before AND after


def has_config_option(section, option):
    """
    Check if the section has this configuration option.

    :param str section: What section to check
    :param str option: What option to check.
    :rtype: bool
    :return: True if and only if the option is defined. It may be `None`
    """
    try:
        return __config.has_option(section, option)
    except AttributeError:
        pass
    _pre_load_config()
    return __config.has_option(section, option)


def config_options(section):
    """
    Return a list of option names for the given section name.

    :param str section: What section to list options for.
    """
    return __config.options(section)


def _check_lines(py_path, line, lines, index, method):
    """
    Support for `_check_python_file`. Gets section and option name.

    :param str line: Line with get_config call
    :param list(str) lines: All lines in the file
    :param int index: index of line with `get_config` call
    :raises ConfigException: If an unexpected or uncovered `get_config` found
    """
    while ")" not in line:
        index += 1
        line += lines[index]
    parts = line[line.find("(", line.find("get_config")) + 1:
                 line.find(")")].split(",")
    section = parts[0].strip().replace("'", "").replace('"', '')
    option = parts[1].strip()
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


def _check_python_file(py_path):
    """
    A testing function to check that all the `get_config` calls work.

    :param str py_path: path to file to be checked
    :raises ConfigException: If an unexpected or uncovered `get_config` found
    """
    with open(py_path, 'r', encoding="utf-8") as py_file:
        lines = py_file.readlines()
        for index, line in enumerate(lines):
            if "get_config_bool(" in line:
                _check_lines(py_path, line, lines, index, get_config_bool)
            if "get_config_float(" in line:
                _check_lines(py_path, line, lines, index, get_config_float)
            if "get_config_int(" in line:
                _check_lines(py_path, line, lines, index, get_config_int)
            if "get_config_str(" in line:
                _check_lines(py_path, line, lines, index, get_config_str)
            if "get_config_str_list(" in line:
                _check_lines(py_path, line, lines, index, get_config_str_list)


def _check_python_files(directory):
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(".py"):
                py_path = os.path.join(root, file_name)
                _check_python_file(py_path)


def _find_double_defaults(repeaters=None):
    """
    Testing function to identify any configuration options in multiple default
    files.

    :param repeaters: List of options that are expected to be repeated.
    :type repeaters: None or list(str)
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
        repeaters = map(config2.optionxform, repeaters)
    for section in config2.sections():
        for option in config2.options(section):
            if config1.has_option(section, option):
                if option not in repeaters:
                    raise ConfigException(
                        f"cfg:{__default_config_files[-1]} "
                        f"repeats [{section}]{option}")


def _check_cfg_file(config1, cfg_path):
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


def _check_cfgs(path):
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


def run_config_checks(directories, *, exceptions=None, repeaters=None):
    """
    Master test.

    :param module:
    :param exceptions:
    :param repeaters:
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
                    _check_python_file(py_path)
