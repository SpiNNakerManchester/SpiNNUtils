import ConfigParser


class CamelCaseConfigParser(ConfigParser.RawConfigParser):

    def optionxform(self, optionstr):
        lower = optionstr.lower()
        return lower.replace("_", "")
