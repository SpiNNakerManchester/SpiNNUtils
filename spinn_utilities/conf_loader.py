# pylint: disable=too-many-arguments
import appdirs
import collections
import ConfigParser
import logging
import os
import string

from spinn_utilities import log
from spinn_utilities.configs import \
    CamelCaseConfigParser, CaseSensitiveParser
from spinn_utilities.configs import \
    NoConfigFoundException, UnexpectedConfigException

logger = logging.getLogger(__name__)


def install_cfg_and_IOError(filename, defaults, config_locations):
    """ Installs a local configuration file based on the templates and raises\
    an exception.

    This method is called when no user configuration file is found.

    It will create a file in the users home directory based on the defaults.\
    Then it prints a helpful message and throws an error with the same message.

    :param filename: Name under which to save the new configuration file
    :type filename: str
    :param defaults: List of full paths to the default configuration files.\
        Each of which MUST have an associated template file with exactly the\
        same path plus .template
    :type defaults: list(str)
    :param config_locations: List of paths where the user configuration files\
        were looked for. Only used for the message
    :type config_locations: list(str)
    :raise spinn_utilities.configs.NoConfigFoundException: Always raised
    """
    home_cfg = os.path.join(os.path.expanduser("~"), ".{}".format(filename))

    with open(home_cfg, "w") as dst:
        for source in defaults:
            with open(source + ".template", "r") as src:
                dst.write(src.read())
                dst.write("\n")
        dst.write("\n# Additional config options can be found in:\n")
        for source in defaults:
            dst.write("# {}\n".format(source))
        dst.write("\n# Copy any additional settings you want to change here "
                  "including section headings\n")

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
    except ConfigParser.NoOptionError:
        pass


def _outdated_config_section(validation_config, defaults, config, skip,
                             user_sections, section):
    """Helper for :py:func:_outdated_config
    """
    if section in user_sections:
        print("Section [{}] should be kept as these need to be set "
              "by the user".format(section))
        return
    elif section not in defaults.sections():
        if validation_config.has_section("DeadSections") and \
                section in validation_config.options("DeadSections"):
            print("Remove the Section [{}]".format(section))
            print("\tThat section is no longer used.")
        else:
            print("Section [{}] does not appear in the defaults so is "
                  "unchecked".format(section))
        return

    different = []
    sames = []
    all_default = True
    for option in config.options(section):
        if option in skip[section]:
            continue
        if not defaults.has_option(section, option):
            print("Unexpected Option [{}] {}".format(section, option))
            all_default = False
        elif config.get(section, option) == defaults.get(section, option):
            sames.append(option)
        else:
            different.append(option)

    if not different:
        if all_default:
            print("Whole section [{}] same as default".format(section))
            print("\tIt can be safely removed")
    elif not sames:
        print("In Section [{}] all options changed".format(section))
        print("\tThis section should be kept")
    elif len(different) < len(sames):
        print("In Section [{}] only options changed are:".format(section))
        print("\t{}".format(different))
        print("\tAll other values can be safely removed")
    else:
        print("In Section [{}] options with default values are:".format(
            section))
        print("\t{}".format(sames))
        print("\tThese can be safely removed")


def _outdated_config(cfg_file, validation_cfg, default_cfg):
    """ Prints why a configuration file is outdated and raises an exception.

    Reads a configuration file by itself (Without others)

    Reports errors in this configuration file based on the validation_cfg and\
    the default_cfg

    Reports any values listed as PreviousValues.\
    These are specific values in specific options no longer supported.\
    For example old algorithm names.

    Checks all sections not defined as UserSections (Default Machine)\
    i.e., ones the user is expected to change

    Any section specifically listed as Dead will be reported

    Any section in the default configuration file is compared, reporting
    * any unexpected values
    * the smaller of values non default or values same as default

    Any other section is ignored as assumed being used by an extension

    :param cfg_file: Path to be checked
    :param validation_cfg: Path containing the validation rules
    :param default_cfg: List of Paths to default_cfg
    :return: an exception
    :rtype: spinn_utilities.configs.UnexpectedConfigException
    """

    try:
        print("Your config file {} is outdated.".format(cfg_file))
        config = CamelCaseConfigParser()
        config.read(cfg_file)

        seen = collections.defaultdict(set)
        if validation_cfg.has_section("PreviousValues"):
            for dead_value in validation_cfg.options("PreviousValues"):
                key = validation_cfg.get("PreviousValues", dead_value)
                sect, opt = key.split("|")
                if config.has_option(sect, opt) and \
                        dead_value in config.get(sect, opt):
                    print("Error in Section [{}] the opt {}".format(sect, opt))
                    print("\t The value below is no longer supported:")
                    print("\t{}".format(dead_value))
                    print("\tUnless you specifically need a none "
                          "default value remove it")
                    seen[sect].add(opt)

        if validation_cfg.has_section("UserSections"):
            user_sections = validation_cfg.options("UserSections")
        else:
            user_sections = ["Machine"]

        for sect in config.sections():
            _outdated_config_section(validation_cfg, default_cfg, config,
                                     seen, user_sections, sect)
        print("Option names are case and underscore insensitive. "
              "So may show in your config file with capitals or underscores.")
    except Exception as e:  # pylint: disable=broad-except
        print("Unexpected error:", e)
    return UnexpectedConfigException(
        "Config file {} is outdated.".format(cfg_file))


def _check_config(cfg, cfg_file, validation_cfg, default_cfg):
    """ Checks the configuration read up to this point to see if it is outdated

    Once one difference is found a full reports is generated and an error\
    raised.

    Any section specifically listed as Dead will cause a error

    Any section in the default_cfg should not have extra values.\
    It will never have less as the default_cfg are in the cfg

    Errors on any values listed as PreviousValues.\
    These are specific values in specific options no longer supported.\
    For example old algorithm names

    :param cfg: Configuration as read in up to this point
    :param cfg_file: Path of last file read in
    :param validation_cfg: Path containing the validation rules
    :param default_cfg: The list of paths to default configurations
    """
    if validation_cfg is None or default_cfg is None:
        return

    # Check for sections registered as dead other none default are ignored
    if validation_cfg.has_section("DeadSections"):
        for sect in validation_cfg.options("DeadSections"):
            if cfg.has_section(sect):
                raise _outdated_config(cfg_file, validation_cfg, default_cfg)

    # check every sect except ones user should change by default machine
    if validation_cfg.has_section("UserSections"):
        user_sections = validation_cfg.options("UserSections")
    else:
        user_sections = ["Machine"]
    # check there are no extra options. default options assumed merged in
    for sect in default_cfg.sections():
        if sect not in user_sections and \
                len(default_cfg.options(sect)) != len(cfg.options(sect)):
            raise _outdated_config(cfg_file, validation_cfg, default_cfg)

    # check for any previous values
    if validation_cfg.has_section("PreviousValues"):
        for dead_value in validation_cfg.options("PreviousValues"):
            key = validation_cfg.get("PreviousValues", dead_value)
            sect, opt = key.split("|")
            if dead_value in cfg.get(sect, opt):
                raise _outdated_config(cfg_file, validation_cfg, default_cfg)


def _read_a_config(config, cfg_file, validation_cfg, default_cfg):
    """ Reads in a configuration file and then directly its machine_spec_file

    :param config: configuration to be updated by the reading of a file
    :param cfg_file: path to file which should be read in
    :param validation_cfg: Path containing the validation rules
    :param default_cfg: The list of paths to default configurations
    :return: None
    """
    config.read(cfg_file)
    _check_config(config, cfg_file, validation_cfg, default_cfg)
    if config.has_option("Machine", "machine_spec_file"):
        machine_spec_file = config.get("Machine", "machine_spec_file")
        config.read(machine_spec_file)
        _check_config(config, machine_spec_file, validation_cfg, default_cfg)
        config.remove_option("Machine", "machine_spec_file")


def _config_locations(filename):
    """Defines the list of places we can get configuration files from.

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
    current_directory_cfg_file = os.path.join(os.curdir, filename)

    # locations to read as well as default later overrides earlier
    return [system_config_cfg_file, user_config_cfg_file,
            user_home_cfg_file, current_directory_cfg_file]


def load_config(filename, defaults, config_parsers=None, validation_cfg=None):
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
    :type config_parsers: list of (str, ConfigParser)
    :param validation_cfg: The list of files to read a validation\
        configuration from. If omitted, no such validation is performed.
    :type validation_cfg: list(str)
    :return: the fully-loaded and checked configuration
    """

    cfg = CamelCaseConfigParser()

    # locations to read as well as default later overrides earlier
    config_locations = _config_locations(filename)
    if not any(os.path.isfile(f) for f in config_locations):
        raise install_cfg_and_IOError(filename, defaults, config_locations)

    cfg.read(defaults)

    if validation_cfg is not None:
        v = CaseSensitiveParser()
        v.read(validation_cfg)
        d = CamelCaseConfigParser()
        d.read(defaults)
    else:
        v = None
        d = None

    for f in config_locations:
        _read_a_config(cfg, f, v, d)

    parsers = list()
    if config_parsers is not None:
        parsers.extend(config_parsers)
    parsers.append(("Logging", logging_parser))

    for section, parser in parsers:
        if cfg.has_section(section):
            parser(cfg)

    # Log which cfg files we read
    print(cfg.read_files)
    logger.info("Read cfg files: %s", string.join(cfg.read_files, ", "))

    return cfg
