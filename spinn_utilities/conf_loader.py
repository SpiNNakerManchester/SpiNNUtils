import appdirs
import shutil
import os
import sys
import logging
import string
from distutils.util import strtobool
from ConfigParser import NoSectionError, NoOptionError, RawConfigParser
from spinn_utilities import log
from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from six import add_metaclass

logger = logging.getLogger(__name__)


def _bool(value):
    """Better version of bool() that handles 'boolean strings'.

    More overhead than standard bool().
    """
    try:
        return bool(strtobool(str(value)))
    except ValueError:
        return bool(value)


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
    except NoOptionError:
        pass


def read_a_config(config, cfg_file):
    """ Reads in a config file and then directly its machine_spec_file

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


def load_config(contextPackage, filename, config_parsers=None):
    """ Load the configuration

    :param config_parsers:\
        The parsers to parse the config with, as a list of\
        (section name, parser); config will only be parsed if the\
        section_name is found in the configuration files already loaded
    :type config_parsers: list of (str, ConfigParserCallback)
    """
    # We don't actually check that the type is right

    contextDir = os.path.dirname(
        os.path.realpath(contextPackage.__file__))
    dotname = "." + filename

    read = list()
    config = _ExtendedConfigParser(read)

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

    if not found_configs:
        print "Unable to find config file in any of the following " \
              "locations: {}\n".format(config_locations)
        # Create a default in the user home directory and get
        # them to update it.
        install_cfg(contextDir, filename)
        sys.exit(2)

    config_locations.insert(0, default_cfg_file)

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


class _ExtendedConfigParser(RawConfigParser):
    def __init__(self, read_files, defaults=None, none_marker="None"):
        RawConfigParser.__init__(self, defaults)
        self._none_marker = none_marker
        self._read_files = read_files

    @property
    def read_files(self):
        """Indicate which files were read when creating this config parser.\
        Only set when this class was instantiated by ConfigurationLoader.
        """
        return self._read_files

    def get_str(self, section, option, default):
        """Get the string value of an option. You can provide a default to be\
        used when the section is absent, the option is absent in the section,\
        or when the user has explicitly set the option to the "None" value (as\
        configured for this object).

        :param section: What section to get the option from.
        :type section: str
        :param option: What option to read.
        :type option: str
        :param default: The default value to use. Will be converted to a\
             string if not already a string *unless* the value is None.
        :type default: str or None
        :return: The option value, or the default.
        :rtype: str (or None, if that is the default)
        """
        d = str(default) if default is not None else None
        try:
            value = self.get(section, option)
            if value == self._none_marker:
                return d
            return str(value)
        except NoSectionError:
            return d
        except NoOptionError:
            return d

    def get_int(self, section, option, default):
        """Get the integer value of an option. You can provide a default to be\
        used when the section is absent, the option is absent in the section,\
        or when the user has explicitly set the option to the "None" value (as\
        configured for this object).

        :param section: What section to get the option from.
        :type section: str
        :param option: What option to read.
        :type option: str
        :param default: The default value to use. Will be converted to an\
             integer if not already an int *unless* the value is None.
        :type default: int or None
        :return: The option value, or the default.
        :rtype: int (or None, if that is the default)
        """
        d = int(default) if default is not None else None
        try:
            value = self.get(section, option)
            if value == self._none_marker:
                return d
            return int(value)
        except NoSectionError:
            return d
        except NoOptionError:
            return d
        except ValueError:
            return d

    def get_float(self, section, option, default):
        """Get the float value of an option. You can provide a default to be\
        used when the section is absent, the option is absent in the section,\
        or when the user has explicitly set the option to the "None" value (as\
        configured for this object).

        :param section: What section to get the option from.
        :type section: str
        :param option: What option to read.
        :type option: str
        :param default: The default value to use. Will be converted to a\
             float if not already a float *unless* the value is None.
        :type default: float or None
        :return: The option value, or the default.
        :rtype: float (or None, if that is the default)
        """
        d = float(default) if default is not None else None
        try:
            value = self.get(section, option)
            if value == self._none_marker:
                return d
            return float(value)
        except NoSectionError:
            return d
        except NoOptionError:
            return d
        except ValueError:
            return d

    def get_bool(self, section, option, default):
        """Get the boolean value of an option. You can provide a default to be\
        used when the section is absent, the option is absent in the section,\
        or when the user has explicitly set the option to the "None" value (as\
        configured for this object).

        :param section: What section to get the option from.
        :type section: str
        :param option: What option to read.
        :type option: str
        :param default: The default value to use. Will be converted to a\
             boolean if not already a bool *unless* the value is None.
        :type default: bool or None
        :return: The option value, or the default.
        :rtype: bool (or None, if that is the default)
        """
        d = _bool(default) if default is not None else None
        try:
            value = self.get(section, option)
            if value == self._none_marker:
                return d
            return _bool(value)
        except NoSectionError:
            return d
        except NoOptionError:
            return d
        except ValueError:
            return d


@add_metaclass(AbstractBase)
class ConfigParserCallback(object):
    __slots__ = []
    @abstractmethod
    def __call__(self, config):
        """Parse a section of the config. The configuration can be updated \
            as required.

        :param config: The configuration containing the section that needs \
            to be parsed.
        :type config: RawConfigParser
        """
