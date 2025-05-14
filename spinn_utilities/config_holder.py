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

from configparser import NoOptionError
import logging
import os
from typing import List, Optional, Tuple

import spinn_utilities.conf_loader as conf_loader
from spinn_utilities.data import UtilsDataView
from spinn_utilities.configs import CamelCaseConfigParser
from spinn_utilities.exceptions import ConfigException
from spinn_utilities.log import (
    FormatAdapter, ConfiguredFilter, ConfiguredFormatter)

logger = FormatAdapter(logging.getLogger(__file__))

# pylint: disable=global-statement
# Any cleaner method than globals would add extra overhead
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


def get_default_cfgs() -> Tuple[str, ...]:
    """
    Returns the default configuration files as a tuple.

    This is a read only values to be used outside of normal operations
    """
    return tuple(__default_config_files)


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


def config_sections() -> List[str]:
    """
    Return a list of section names

    """
    if __config is None:
        raise ConfigException("configuration not loaded")
    return __config.sections()


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


def get_report_path(
        option: str, section: str = "Reports", n_run: Optional[int] = None,
        is_dir: bool = False) -> str:
    """
    Gets and fixes the path for this option

    If the cfg path is relative it will be joined with the run_dir_path.

    Creates the path's directory if it does not exist.

    (n_run) and (reset_str) will be replaced

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


def get_timestamp_path(option: str, section: str = "Reports") -> str:
    """
    Gets and fixes the path for this option

    If the cfg path is relative it will be joined with the timestamp_path.

    Creates the path's directory if it does not exist.

    Later updates may replace bracketed expressions as needed
    so avoid using brackets in file names

    :param option: cfg option name
    :param section: cfg section. Needed if not Reports
    :param n_run: If provided will be used instead of the current run number
    :return: An unchecked absolute path to the file or directory
    """

    path = get_config_str(section, option)
    if not os.path.isabs(path):
        path = os.path.join(UtilsDataView.get_timestamp_dir_path(), path)

    folder, _ = os.path.split(path)
    os.makedirs(folder, exist_ok=True)

    return path
