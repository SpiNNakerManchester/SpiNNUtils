try:
    from ConfigParser import RawConfigParser
except ImportError:  # pragma: no cover
    from configparser import RawConfigParser


class CaseSensitiveParser(RawConfigParser):

    def optionxform(self, optionstr):
        return optionstr
