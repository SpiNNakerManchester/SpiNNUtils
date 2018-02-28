try:
    from ConfigParser import RawConfigParser as _parser
except ImportError:
    from configparser import RawConfigParser as _parser


class CaseSensitiveParser(_parser):

    def optionxform(self, optionstr):
        return optionstr
