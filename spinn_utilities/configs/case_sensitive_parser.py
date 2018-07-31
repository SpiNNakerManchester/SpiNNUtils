from six.moves import configparser


class CaseSensitiveParser(configparser.RawConfigParser):
    def optionxform(self, optionstr):
        """ Performs no transformation of option strings.
        """
        return optionstr
