from ConfigParser import RawConfigParser


class CaseSensitiveParser(RawConfigParser):

    def optionxform(self, optionstr):
        return optionstr
