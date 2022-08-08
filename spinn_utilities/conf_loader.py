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

import appdirs
import configparser
import logging
import os
from spinn_utilities.log import FormatAdapter
from spinn_utilities import log
from spinn_utilities.configs import (
    CamelCaseConfigParser, ConfigTemplateException,
    NoConfigFoundException, UnexpectedConfigException)
logger = FormatAdapter(logging.getLogger(__name__))


def install_cfg_and_IOError(filename, defaults, config_locations):
    """ Installs a local configuration file based on the templates and raises\
        an exception.

    This method is called when no user configuration file is found.

    It will create a file in the users home directory based on the defaults.\
    Then it prints a helpful message and throws an error with the same message.

    :param filename: Name under which to save the new configuration file
    :type filename: str
    :param defaults: List of full paths to the default configuration files.\
        Each of which *must* have an associated template file with exactly the\
        same path plus `.template`.
    :type defaults: list(str)
    :param config_locations: List of paths where the user configuration files\
        were looked for. Only used for the message
    :type config_locations: list(str)
    :raise spinn_utilities.configs.NoConfigFoundException: Always raised
    """
    home_cfg = os.path.join(os.path.expanduser("~"), ".{}".format(filename))

    found = False
    with open(home_cfg, "w", encoding="utf-8") as dst:
        for source in defaults:
            template = source + ".template"
            if os.path.isfile(template):
                if found:
                    raise ConfigTemplateException(
                        f"Second template found at {template}")
                with open(source + ".template", "r", encoding="utf-8") as src:
                    dst.write(src.read())
                    dst.write("\n")
                    found = True
        if not found:
            if defaults:
                raise ConfigTemplateException(
                    f"No template file found for {defaults}")
            else:
                raise ConfigTemplateException(
                    f"No default cfg files found. "
                    f"New {home_cfg} will be empty")

        dst.write("\n# Additional config options can be found in:\n")
        for source in defaults:
            dst.write("# {}\n".format(source))
        dst.write("\n# Copy any additional settings you want to change"
                  " here including section headings\n")

    msg = f"Unable to find config file in any of the following locations: \n" \
          f"{config_locations}\n" \
          f"********************************************************\n" \
          f"{home_cfg} has been created. \n" \
          f"Please edit this file and change \"None\" after \"machineName\" " \
          f"to the hostname or IP address of your SpiNNaker board, " \
          f"and change \"None\" after \"version\" to the version of " \
          f"SpiNNaker hardware you are running on:\n" \
          f"[Machine]\n" \
          f"machineName = None\n" \
          f"version = None\n" \
          f"***********************************************************\n"
    print(msg)
    return NoConfigFoundException(msg)


def logging_parser(config):
    """ Create the root logger with the given level.

    Create filters based on logging levels

    .. note::
        You do not normally need to call this function; it is used\
        automatically to parse Logging configuration sections.
    """
    try:
        if config.getboolean("Logging", "instantiate"):
            logging.basicConfig(level=0)

        for handler in logging.root.handlers:
            handler.addFilter(log.ConfiguredFilter(config))
            handler.setFormatter(log.ConfiguredFormatter(config))
    except configparser.NoOptionError:
        pass


def _check_config(cfg_file, default_configs, strict):
    """ Checks the configuration read up to this point to see if it is outdated

    Once one difference is found a full reports is generated and an error\
    raised.

    Any section specifically listed as Dead will cause a error

    Any section in the default_cfg should not have extra values.\
    It will never have less as the default_cfg are in the cfg

    Errors on any values listed as PreviousValues.\
    These are specific values in specific options no longer supported.\
    For example old algorithm names

    :param str cfg_file: Path of last file read in
    :param CamelCaseConfigParser default_configs:
        configuration with just the default files in
    :param bool strict: Flag to say an exception should be raised
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


def _read_a_config(configs, cfg_file, default_configs, strict):
    """ Reads in a configuration file and then directly its machine_spec_file

    :param CamelCaseConfigParser configs:
        configuration to be updated by the reading of a file
    :param str cfg_file: path to file which should be read in
    :param CamelCaseConfigParser default_configs:
        configuration with just the default files in
    :param bool strict: Flag to say checker should raise an exception
    :return: None
    """
    _check_config(cfg_file, default_configs, strict)
    configs.read(cfg_file)
    if configs.has_option("Machine", "machine_spec_file"):
        machine_spec_file = configs.get("Machine", "machine_spec_file")
        _check_config(machine_spec_file, default_configs, strict)
        configs.read(machine_spec_file)
        configs.remove_option("Machine", "machine_spec_file")


def _config_locations(filename):
    """ Defines the list of places we can get configuration files from.

    :param filename: The local name of the config file, e.g., 'spynnaker.cfg'
    :type filename: str
    :return: list of fully-qualified filenames
    :rtype: list(str)
    """
    dotname = "." + filename

    # locations to read as well as default later overrides earlier
    system_config_cfg_file = os.path.join(appdirs.site_config_dir(), dotname)
    user_config_cfg_file = os.path.join(appdirs.user_config_dir(), dotname)
    user_home_cfg_file = os.path.join(os.path.expanduser("~"), dotname)

    # locations to read as well as default later overrides earlier
    return [system_config_cfg_file, user_config_cfg_file,
            user_home_cfg_file]


def load_config(filename, defaults, config_parsers=None):
    """ Load the configuration.

    :param filename: The base name of the configuration file(s). Should not\
        include any path components.
    :type filename: str
    :param defaults: The list of files to get default configurations from.
    :type defaults: list(str)
    :param config_parsers:\
        The parsers to parse the sections of the configuration file with, as\
        a list of (section name, parser); a configuration section will only\
        be parsed if the section_name is found in the configuration files\
        already loaded. The standard logging parser is appended to (a copy\
        of) this list.
    :type config_parsers: list(tuple(str, ConfigParser))
    :return: the fully-loaded and checked configuration
    """

    configs = CamelCaseConfigParser()

    # locations to read as well as default later overrides earlier
    config_locations = _config_locations(filename)
    if not any(os.path.isfile(f) for f in config_locations):
        if defaults:
            raise install_cfg_and_IOError(
                filename, defaults, config_locations)
        else:
            logger.error("No default cfg files provided")

    configs.read(defaults)

    default_configs = CamelCaseConfigParser()
    default_configs.read(defaults)

    for cfg_file in config_locations:
        _read_a_config(configs, cfg_file, default_configs, False)
    cfg_file = os.path.join(os.curdir, filename)
    _read_a_config(configs, cfg_file, default_configs, True)

    parsers = list()
    if config_parsers is not None:
        parsers.extend(config_parsers)
    parsers.append(("Logging", logging_parser))

    for section, parser in parsers:
        if configs.has_section(section):
            parser(configs)

    # Log which configs files we read
    print(configs.read_files)
    logger.info("Read configs files: %s", ", ".join(configs.read_files))

    return configs
