import appdirs
import shutil
import os
import ConfigParser
import sys
import logging
import string
from spinn_utilities import log

logger = logging.getLogger(__name__)


def install_cfg_and_IOError(filename, defaults, config_locations):
    home_cfg = os.path.join(os.path.expanduser("~"), ".{}".format(filename))

    with (open(home_cfg, "w")) as destination:
        for source in defaults:
            template = source + ".template"
            with open(source, "r") as source_file:
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
          "to the hostname or IP address of your SpiNNaker board, and change " \
          "\"None\" after \"version\" to the version of SpiNNaker hardware " \
          "you are running on:\n" \
          "[Machine]\n" \
          "machineName = None\n" \
          "version = None\n" \
          "***********************************************************\n" \
          "".format(config_locations, home_cfg)
    print msg
    raise IOError(msg)


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


def read_a_config(config, cfg_file):
    """ Reads in a config file andthen directly its machine_spec_file

    :param config: config to do the reading
    :param cfg_file: path to file which should be read in
    :return: list of files read including and machione_spec_files
    """
    read_ok = config.read(cfg_file)
    if config.has_option("Machine", "machine_spec_file"):
        machine_spec_file_path = config.get("Machine", "machine_spec_file")
        read_ok.extend(config.read(machine_spec_file_path))
        config.remove_option("Machine", "machine_spec_file")
    return read_ok


def checked_path(directory, filename, old_filename, dot):
    if dot:
        filename = ".{}".format(filename)
    current_path = os.path.join(directory, filename)
    if not os.path.exists(current_path) and old_filename is not None:
        if dot:
            old_file_name = ".{}".format(old_filename)
        old_path = os.path.join(directory, old_filename)
        if os.path.exists(old_path):
            msg = "Config file name has changed from {} to {}\n" \
                  "Found old config {}\n" \
                  "Please rename it to {}" \
                  "".format(old_filename, filename, old_path, current_path)
            print msg
            raise IOError(msg)
    return current_path


def checked_path_copy(directory, filename, old_filename, dot):
    if dot:
        filename = ".{}".format(filename)
    current_path = os.path.join(directory, filename)
    if not os.path.exists(current_path) and old_filename is not None:
        if dot:
            old_file_name = ".{}".format(old_filename)
        old_path = os.path.join(directory, old_filename)
        if os.path.exists(old_path):
            shutil.copyfile(old_path, current_path)
            logger.warn("{} copied to {}".format(old_path, current_path))
    return current_path


def load_config(filename, defaults, old_filename=None, config_parsers=None):
    """ Load the configuration

    :param config_parsers:\
        The parsers to parse the config with, as a list of\
        (section name, parser); config will only be parsed if the\
        section_name is found in the configuration files already loaded
    :type config_parsers: list of (str, ConfigParser)
    """

    config = ConfigParser.RawConfigParser()

    # locations to read as well as default later overrides earlier
    config_locations = []
    config_locations.append(checked_path(appdirs.site_config_dir(),
                                         filename, old_filename, True))
    config_locations.append(checked_path(appdirs.user_config_dir(),
                                         filename, old_filename, True))
    config_locations.append(checked_path(os.path.expanduser("~"),
                                         filename, old_filename, True))
    config_locations.append(checked_path(os.curdir,
                                         filename, old_filename, False))

    found_configs = False
    for possible_config_file in config_locations:
        if os.path.isfile(possible_config_file):
            found_configs = True

    if not found_configs:
        install_cfg_and_IOError(filename, defaults, config_locations)

    config_locations[0:0] = defaults

    read = list()
    for possible_config_file in config_locations:
        read.extend(read_a_config(config, possible_config_file))

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
