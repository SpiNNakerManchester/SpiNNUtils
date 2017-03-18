import shutil
import os
import ConfigParser
import sys
import logging
import string
from distutils.util import strtobool
from spinn_utilities import log


class ConfigurationLoader():
    """ Utility for loading configuration files from a range of paths,\
        including the user home directory and the current working directory
    """

    def __init__(self, contextPackage, filename):
        """

        :param contextPackage:\
            The package that contains the default configuration
        :param filename:\
            The name of the configuration file to be found in the paths\
            searched (including the default package)
        """
        self._contextPackage = contextPackage
        self._contextDir = os.path.dirname(os.path.realpath(
            contextPackage.__file__))
        self._filename = filename
        try:
            self._in_read_the_docs = bool(strtobool(
                os.environ.get("READTHEDOCS", "False")))
        except:
            self._in_read_the_docs = False

    def print_message(self, filename):
        print "************************************"
        print("{} has been created.  Please edit this file and change \"None\""
              " after \"machineName\" to the hostname or IP address of your"
              " SpiNNaker board, and change \"None\" after \"version\" to the"
              " version of SpiNNaker hardware you are running on:".format(
                  filename))
        print "[Machine]"
        print "machineName = None"
        print "version = None"
        print "************************************"

    def _install_cfg(self):
        template_cfg = os.path.join(self._contextDir,
                                    "{}.template".format(self._filename))
        home_cfg = os.path.expanduser("~/.{}".format(self._filename))
        shutil.copyfile(template_cfg, home_cfg)
        self.print_message(home_cfg)

    def _logging_parser(self, config):
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

    def _machine_spec_parser(self, config):
        """ Load any cross-referenced machine specification file.
        """
        if not config.has_option("Machine", "machine_spec_file"):
            return None
        machine_spec_file_path = config.get("Machine", "machine_spec_file")
        config.read(machine_spec_file_path)
        return machine_spec_file_path

    def load_config(self, config_parsers=None):
        """ Load the configuration

        :param config_parsers:\
            The parsers to parse the config with, as a list of\
            (section name, parser); config will only be parsed if the\
            section_name is found in the configuration files already loaded
        :type config_parsers: list of (str, ConfigParser)
        """
        config = ConfigParser.RawConfigParser()

        # When the config is being loaded in read-the-docs, skip loading
        # as this is not needed to generate documents
        if self._in_read_the_docs:
            return config
        default = os.path.join(self._contextDir, self._filename)
        spynnaker_user = os.path.expanduser("~/.{}".format(self._filename))
        config_locations = [spynnaker_user, self._filename]

        found_configs = False
        for possible_config_file in config_locations:
            if os.path.isfile(possible_config_file):
                found_configs = True
                os.path.abspath(possible_config_file)

        with open(default) as f:
            config.readfp(f)

        if not found_configs:

            # Create a default spynnaker.cfg in the user home directory and get
            # them to update it.
            self._install_cfg()
            sys.exit(2)

        read = config.read(config_locations)
        read.append(default)
        parsers = list()
        if config_parsers is not None:
            parsers.extend(config_parsers)
        parsers.append(("Logging", self._logging_parser))
        parsers.append(("Machine", self._machine_spec_parser))

        for (section, parser) in parsers:
            if config.has_section(section):
                result = parser(config)
                if result is not None:
                    read.append(result)

        # Log which config files we read
        logger = logging.getLogger(self._contextPackage.__name__)
        logger.info("Read config files: %s" % string.join(read, ", "))

        return config
