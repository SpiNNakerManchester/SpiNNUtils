from six.moves import configparser


class CaseSensitiveParser(configparser.RawConfigParser):
    def optionxform(self, optionstr):
        return optionstr
