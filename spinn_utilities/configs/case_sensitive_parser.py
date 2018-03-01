try:
    from ConfigParser import RawConfigParser
except ImportError:
    from configparser import RawConfigParser


class CaseSensitiveParser(RawConfigParser):

    def optionxform(self, optionstr):
        return optionstr
