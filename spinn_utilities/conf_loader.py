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
from typing import Callable, List

import appdirs
from typing_extensions import TypeAlias

from spinn_utilities import log
from spinn_utilities.configs import (
    CamelCaseConfigParser, UnexpectedConfigException)

logger = log.FormatAdapter(logging.getLogger(__name__))
_SectionParser: TypeAlias = Callable[[CamelCaseConfigParser], None]


def _check_config(cfg_file: str, default_configs: CamelCaseConfigParser,
                  strict: bool) -> None:
    """
    Checks the configuration read up to this point to see if it is outdated.

    Once one difference is found a full reports is generated and an error
    raised.

    Any section specifically listed as Dead will cause a error

    Any section in the default_cfg should not have extra values.
    It will never have less as the default_cfg are in the configuration.

    Errors on any values listed as PreviousValues.
    These are specific values in specific options no longer supported.
    For example old algorithm names.

    :param cfg_file: Path of last file read in
    :param default_configs:
        configuration with just the default files in
    :param strict: Flag to say an exception should be raised
    """
    if not default_configs.sections():  # empty
        logger.warning("Can not validate cfg files as no default.")
        return
    configs = CamelCaseConfigParser()
    configs.read(cfg_file)
    msg = ""
    for section in configs.sections():
        if default_configs.has_section(section):
            for option in configs.options(section):
                if not default_configs.has_option(section, option):
                    msg += f"Unexpected Option: [{section}]{option}\n"
        else:
            msg += f"Unexpected Section: [{section}]\n"
    if msg:
        msg += f"found in {cfg_file}"
        if strict:
            raise UnexpectedConfigException(msg)
        else:
            logger.warning(msg)


def _read_a_config(
        configuration: CamelCaseConfigParser, cfg_file: str,
        default_configs: CamelCaseConfigParser, strict: bool) -> None:
    """
    Reads in a configuration file and then directly its `machine_spec_file`.

    :param configuration:
        configuration to be updated by the reading of a file
    :param cfg_file: path to file which should be read in
    :param default_configs:
        configuration with just the default files in
    :param strict: Flag to say checker should raise an exception
    """
    _check_config(cfg_file, default_configs, strict)
    configuration.read(cfg_file)
    if configuration.has_option("Machine", "machine_spec_file"):
        machine_spec_file = configuration.get("Machine", "machine_spec_file")
        _check_config(machine_spec_file, default_configs, strict)
        configuration.read(machine_spec_file)
        configuration.remove_option("Machine", "machine_spec_file")


def _config_locations(filename: str) -> List[str]:
    """
    Defines the list of places we can get configuration files from.

    :param filename:
        The local name of the configuration file, e.g., 'spynnaker.cfg'
    :return: list of fully-qualified filenames
    """
    dotname = "." + filename

    # locations to read as well as default later overrides earlier
    system_config_cfg_file = os.path.join(appdirs.site_config_dir(), dotname)
    user_config_cfg_file = os.path.join(appdirs.user_config_dir(), dotname)
    user_home_cfg_file = os.path.join(os.path.expanduser("~"), dotname)

    # locations to read as well as default later overrides earlier
    return [system_config_cfg_file, user_config_cfg_file,
            user_home_cfg_file]


def load_defaults(defaults: List[str]) -> CamelCaseConfigParser:
    """
    Load the default configuration.

    :param defaults:
        The list of files to get default configurations from.
    :return: the fully-loaded configuration
    """
    default_configs = CamelCaseConfigParser()
    default_configs.read(defaults)
    return default_configs


def load_config(
        user_cfg: str, defaults: List[str]) -> CamelCaseConfigParser:
    """
    Load the configuration.

    :param user_cfg:
        Path to existing user cfg. This file must exist.
    :param defaults:
        The list of files to get default configurations from.
    :return: the fully-loaded and checked configuration
    """
    configs = load_defaults(defaults)
    default_configs = load_defaults(defaults)

    _read_a_config(configs, user_cfg, default_configs, False)
    filename = os.path.basename(user_cfg)
    cfg_file = os.path.join(os.curdir, filename)
    _read_a_config(configs, cfg_file, default_configs, True)

    # Log which configs files we read
    print(configs.read_files)
    logger.info("Read configs files: {}", ", ".join(configs.read_files))

    return configs
