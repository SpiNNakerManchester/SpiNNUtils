import appdirs
import ConfigParser
import os

import logging
import string
from spinn_utilities import log
from spinn_utilities.camel_case_config_parser import CamelCaseConfigParser
from spinn_utilities.unexpected_config_exception import \
    UnexpectedConfigException
from spinn_utilities.no_config_found_exception import NoConfigFoundException

logger = logging.getLogger(__name__)


def install_cfg_and_IOError(filename, defaults, config_locations):
    home_cfg = os.path.join(os.path.expanduser("~"), ".{}".format(filename))

    with (open(home_cfg, "w")) as destination:
        for source in defaults:
            template = source + ".template"
            with open(template, "r") as source_file:
                destination.write(source_file.read())
                destination.write("\n")
        destination.write("\n# Additional config options can be found in:\n")
        for source in defaults:
            destination.write("# {}\n".format(source))
        destination.write("\n# Copy any additional settings you want to "
                          "change here including section headings\n")

    msg = "Unable to find config file in any of the following locations: \n" \
          "{}\n" \
          "********************************************************\n" \
          "{} has been created. \n" \
          "Please edit this file and change \"None\" after \"machineName\" " \
          "to the hostname or IP address of your SpiNNaker board, " \
          "and change \"None\" after \"version\" to the version of " \
          "SpiNNaker hardware you are running on:\n" \
          "[Machine]\n" \
          "machineName = None\n" \
          "version = None\n" \
          "***********************************************************\n" \
          "".format(config_locations, home_cfg)
    print msg
    raise NoConfigFoundException(msg)


def logging_parser(config):
    """ Create the root logger with the given level.

        Create filters based on logging levels
    """
    try:
        if config.getboolean("Logging", "instantiate"):
            logging.basicConfig(level=0)

        for handler in logging.root.handlers:
            handler.addFilter(log.ConfiguredFilter(config))
            handler.setFormatter(log.ConfiguredFormatter(config))
    except ConfigParser.NoOptionError:
        pass


def check_config(config, cfg_file, default_config_names):
    for section in default_config_names:
        if (len(default_config_names[section]) != len(
                config.options(section))):
            for name in config.options(section):
                if name not in default_config_names[section] and \
                                name != "machinespecfile":
                    msg = "Unexpected config {} found in section {} " \
                          "found in {}".format(name, section, cfg_file)
                    raise UnexpectedConfigException(msg)


def read_a_config(config, cfg_file, default_config_names):
    """ Reads in a config file and then directly its machine_spec_file

    :param config: config to do the reading
    :param cfg_file: path to file which should be read in
    :return: list of files read including and machione_spec_files
    """
    read_ok = config.read(cfg_file)
    check_config(config, cfg_file, default_config_names)
    if config.has_option("Machine", "machine_spec_file"):
        machine_spec_file_path = config.get("Machine", "machine_spec_file")
        read_ok.extend(config.read(machine_spec_file_path))
        check_config(config, machine_spec_file_path, default_config_names)
        config.remove_option("Machine", "machine_spec_file")
    return read_ok


def load_config(filename, defaults, config_parsers=None,
                check_for_extra_values=True):
    """ Load the configuration

    :param config_parsers:\
        The parsers to parse the config with, as a list of\
        (section name, parser); config will only be parsed if the\
        section_name is found in the configuration files already loaded
    :type config_parsers: list of (str, ConfigParser)
    """

    config = CamelCaseConfigParser()
    dotname = "." + filename

    # locations to read as well as default later overrides earlier
    config_locations = []
    system_config_cfg_file = os.path.join(appdirs.site_config_dir(), dotname)
    user_config_cfg_file = os.path.join(appdirs.user_config_dir(), dotname)
    user_home_cfg_file = os.path.join(os.path.expanduser("~"), dotname)
    current_directory_cfg_file = os.path.join(os.curdir, filename)

    # locations to read as well as default later overrides earlier
    config_locations = [system_config_cfg_file, user_config_cfg_file,
                        user_home_cfg_file, current_directory_cfg_file]

    found_configs = False
    for possible_config_file in config_locations:
        if os.path.isfile(possible_config_file):
            found_configs = True

    if not found_configs:
        install_cfg_and_IOError(filename, defaults, config_locations)

    read = list()
    default_config_names = dict()
    for default in defaults:
        read.extend(read_a_config(config, default, default_config_names))

    if check_for_extra_values:
        for section in config.sections():
            default_config_names[section] = config.options(section)

    for possible_config_file in config_locations:
        read.extend(read_a_config(config, possible_config_file,
                                  default_config_names))

    parsers = list()
    if config_parsers is not None:
        parsers.extend(config_parsers)
    parsers.append(("Logging", logging_parser))

    for (section, parser) in parsers:
        if config.has_section(section):
            parser(config)

    # Log which config files we read
    logger.info("Read config files: %s" % string.join(read, ", "))

    return config
