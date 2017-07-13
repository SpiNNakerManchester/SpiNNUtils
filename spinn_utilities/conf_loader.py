import appdirs
import collections
import ConfigParser
import logging
import os
import string
import sys

from spinn_utilities import log
from spinn_utilities.camel_case_config_parser import CamelCaseConfigParser
from spinn_utilities.case_sensitive_parser import CaseSensitiveParser
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


def outdated_config(cfg_file, validation_config, default_config):
    try:
        print "Your config file {} is outdated.".format(cfg_file)
        config = CamelCaseConfigParser()
        config.read(cfg_file)

        previous_sections = collections.defaultdict(set)
        if validation_config.has_section("PreviousValues"):
            for dead_value in validation_config.options("PreviousValues"):
                key = validation_config.get("PreviousValues", dead_value)
                (section, option) = key.split("|")
                if config.has_option(section, option) and \
                        dead_value in config.get(section, option):
                    print "Error in Section [{}] the option {}" \
                          "".format(section, option)
                    print "\t The value below is no longer supported:"
                    print "\t{}".format(dead_value)
                    print "\tUnless you specifically need a none " \
                          "default value remove it"
                    previous_sections[section].add(option)

        if validation_config.has_section("UserSections"):
            user_sections = validation_config.options("UserSections")
        else:
            user_sections = ["Machine"]

        for section in config.sections():
            if section in user_sections:
                print "Section [{}] should be kept as these need to be set " \
                      "by the user".format(section)
            elif section not in default_config.sections():
                if validation_config.has_section("DeadSections"):
                    if section in validation_config.options("DeadSections"):
                        print "Remove the Section [{}]".format(section)
                        print "\tThat section is no longer used."
                        break
                print "Section [{}] does not appear in the defaults so is " \
                      "unchecked".format(section)
            else:
                different = []
                sames = []
                all_default = True
                for option in config.options(section):
                    if option in previous_sections[section]:
                        pass
                    elif default_config.has_option(section, option):
                        if config.get(section, option) == \
                                default_config.get(section, option):
                            sames.append(option)
                        else:
                            different.append(option)
                    else:
                        print "Unexpected Option [{}] {}" \
                              "".format(section, option)
                        all_default = False
                if len(different) == 0:
                    if all_default:
                        print "Whole section [{}] same as default" \
                              "".format(section)
                        print "\tIt can be safely removed"
                elif len(sames) == 0:
                    print "In Section [{}] all options changed".format(section)
                    print "\tThis section should be kept"
                elif len(different) < len(sames):
                    print "In Section [{}] only options changed are:" \
                          "".format(section)
                    print "\t{}".format(different)
                    print "\tAll other values can be safelty removed"
                else:
                    print "In Section [{}] options with default values are:" \
                          "".format(section)
                    print "\t{}".format(sames)
                    print "\tThese can be safely removed"
        print "Option names are case and underscore insenitive. " \
              "So may show in your cfg file with capitals or underscores."
    except:
        print "Unexpected error:", sys.exc_info()[0]
        msg = "Config file {} is outdated.".format(cfg_file)
        raise UnexpectedConfigException(msg)


def check_config(config, cfg_file, validation_config=None,
                 default_config=None):
    if validation_config is None or default_config is None:
        return

    # Check for sections registered as dead other none default are ignored
    if validation_config.has_section("DeadSections"):
        for dead_section in validation_config.options("DeadSections"):
            if config.has_section(dead_section):
                raise outdated_config(cfg_file, validation_config,
                                      default_config)

    # check every section except ones user should change by default machine
    if validation_config.has_section("UserSections"):
        user_sections = validation_config.options("UserSections")
    else:
        user_sections = ["Machine"]
    # check there are no extra options. default options assumed merged in
    for section in default_config.sections():
        if section not in user_sections and \
                (len(default_config.options(section)) !=
                 len(config.options(section))):
            raise outdated_config(cfg_file, validation_config, default_config)

    # check for any previous values
    if validation_config.has_section("PreviousValues"):
        for dead_value in validation_config.options("PreviousValues"):
            key = validation_config.get("PreviousValues", dead_value)
            (section, option) = key.split("|")
            if dead_value in config.get(section, option):
                raise outdated_config(cfg_file, validation_config,
                                      default_config)


def read_a_config(config, cfg_file, validation_config=None,
                  default_config=None):
    """ Reads in a config file and then directly its machine_spec_file

    :param config: config to do the reading
    :param cfg_file: path to file which should be read in
    :return: list of files read including and machione_spec_files
    """
    read_ok = config.read(cfg_file)
    check_config(config, cfg_file, validation_config, default_config)
    if config.has_option("Machine", "machine_spec_file"):
        machine_spec_file_path = config.get("Machine", "machine_spec_file")
        read_ok.extend(config.read(machine_spec_file_path))
        check_config(config, machine_spec_file_path, validation_config,
                     default_config)
        config.remove_option("Machine", "machine_spec_file")
    return read_ok


def load_config(filename, defaults, config_parsers=None, validation_cfg=None):
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
    read.extend(config.read(defaults))

    if validation_cfg is not None:
        validation_config = CaseSensitiveParser()
        validation_config.read(validation_cfg)
        default_config = CamelCaseConfigParser()
        default_config.read(defaults)
    else:
        validation_config = None
        default_config = None

    for possible_config_file in config_locations:
        read.extend(read_a_config(config, possible_config_file,
                                  validation_config, default_config))

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
