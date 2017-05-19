import appdirs
import shutil
import os
import ConfigParser
import sys
import logging
import string
from spinn_utilities import log

logger = logging.getLogger(__name__)


def install_cfg(contextDir, filename):
    template_file = filename + ".template"
    template_cfg = os.path.join(contextDir, template_file)
    dotname = "." + filename
    home_cfg = os.path.join(os.path.expanduser("~"), dotname)
    shutil.copyfile(template_cfg, home_cfg)
    print "************************************"
    print("{} has been created. \n"
          "Please edit this file and change \"None\""
          " after \"machineName\" to the hostname or IP address of your"
          " SpiNNaker board, and change \"None\" after \"version\" to the"
          " version of SpiNNaker hardware you are running "
          "on:".format(home_cfg))
    print "[Machine]"
    print "machineName = None"
    print "version = None"
    print "************************************"


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
    return None


def machine_spec_parser(config):
    """ Load any cross-referenced machine specification file.
    """
    if not config.has_option("Machine", "machine_spec_file"):
        return None
    machine_spec_file_path = config.get("Machine", "machine_spec_file")
    read_ok = config.read(machine_spec_file_path)
    if len(read_ok) == 1:
        return read_ok[0]
    return None


def load_config(contextPackage, filename, config_parsers=None):
    """ Load the configuration

    :param config_parsers:\
        The parsers to parse the config with, as a list of\
        (section name, parser); config will only be parsed if the\
        section_name is found in the configuration files already loaded
    :type config_parsers: list of (str, ConfigParser)
    """

    contextDir = os.path.dirname(
        os.path.realpath(contextPackage.__file__))
    dotname = "." + filename

    config = ConfigParser.RawConfigParser()

    # Search path for config files (lowest to highest priority)
    default_cfg_file = os.path.join(contextDir, filename)
    system_config_cfg_file = os.path.join(appdirs.site_config_dir(), dotname)
    user_config_cfg_file = os.path.join(appdirs.user_config_dir(), dotname)
    user_home_cfg_file = os.path.join(os.path.expanduser("~"), dotname)
    current_directory_cfg_file = os.path.join(os.curdir, filename)

    # locations to read as well as default later overrides earlier
    config_locations = [system_config_cfg_file,
                        user_config_cfg_file,
                        user_home_cfg_file,
                        current_directory_cfg_file]

    found_configs = False
    for possible_config_file in config_locations:
        if os.path.isfile(possible_config_file):
            found_configs = True
            os.path.abspath(possible_config_file)

    if not found_configs:
        print "Unable to find config file in any of the following " \
              "locations: {}\n".format(config_locations)
        # Create a default in the user home directory and get
        # them to update it.
        install_cfg(contextDir, filename)
        sys.exit(2)

    with open(default_cfg_file) as f:
        config.readfp(f)

    read = config.read(config_locations)
    read.insert(0, default_cfg_file)
    parsers = list()
    if config_parsers is not None:
        parsers.extend(config_parsers)
    parsers.append(("Logging", logging_parser))
    parsers.append(("Machine", machine_spec_parser))

    for (section, parser) in parsers:
        if config.has_section(section):
            result = parser(config)
            if result is not None:
                read.append(result)

    # Log which config files we read
    logger.info("Read config files: %s" % string.join(read, ", "))

    return config
