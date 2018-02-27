from ConfigParser import RawConfigParser
import distutils.util


class CamelCaseConfigParser(RawConfigParser):
    # RawConfigParser is a classobj in Python 2.7, not a type (i.e., it
    # doesn't inherit from object), and so cannot be used with super().

    def optionxform(self, optionstr):
        lower = optionstr.lower()
        return lower.replace("_", "")

    def __init__(self, defaults=None, none_marker="None"):
        RawConfigParser.__init__(self, defaults)
        self._none_marker = none_marker
        self.read_files = list()

    def read(self, filenames):
        new_files = RawConfigParser.read(self, filenames)
        self.read_files.extend(new_files)
        return new_files

    @property
    def read_files(self):
        return self.read_files

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
            return bool(distutils.util.strtobool(str(value)))
        except ValueError:
            return bool(value)
