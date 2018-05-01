from six.moves import configparser
import distutils.util as _du  # pylint: disable=import-error, no-name-in-module


# pylint: disable=slots-on-old-class
class CamelCaseConfigParser(configparser.RawConfigParser):
    # RawConfigParser is a classobj in Python 2.7, not a type (i.e., it
    # doesn't inherit from object), and so cannot be used with super().
    __slots__ = ["_none_marker", "_read_files"]

    def optionxform(self, optionstr):
        lower = optionstr.lower()
        return lower.replace("_", "")

    def __init__(self, defaults=None, none_marker="None"):
        configparser.RawConfigParser.__init__(self, defaults)
        self._none_marker = none_marker
        self._read_files = list()

    def read(self, filenames):
        new_files = configparser.RawConfigParser.read(self, filenames)
        self._read_files.extend(new_files)
        return new_files

    @property
    def read_files(self):
        return self._read_files

    def get_str(self, section, option):
        """Get the string value of an option.

        :param section: What section to get the option from.
        :type section: str
        :param option: What option to read.
        :type option: str
        :return: The option value
        :rtype: str or None
        """
        value = self.get(section, option)
        if value == self._none_marker:
            return None
        return value

    def get_int(self, section, option):
        """Get the integer value of an option.

        :param section: What section to get the option from.
        :type section: str
        :param option: What option to read.
        :type option: str
        :return: The option value
        :rtype: int
        """
        value = self.get(section, option)
        if value == self._none_marker:
            return None
        return int(value)

    def get_float(self, section, option):
        """Get the float value of an option.

        :param section: What section to get the option from.
        :type section: str
        :param option: What option to read.
        :type option: str
        :return: The option value.
        :rtype: float
        """
        value = self.get(section, option)
        if value == self._none_marker:
            return None
        return float(value)

    def get_bool(self, section, option):
        """Get the boolean value of an option.

        :param section: What section to get the option from.
        :type section: str
        :param option: What option to read.
        :type option: str
        :return: The option value.
        :rtype: bool
        """
        value = self.get(section, option)
        if value == self._none_marker:
            return None
        try:
            return bool(_du.strtobool(str(value)))
        except ValueError:
            return bool(value)
