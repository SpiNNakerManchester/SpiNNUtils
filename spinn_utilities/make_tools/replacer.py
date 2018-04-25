import logging
import os
from spinn_utilities.log import FormatAdapter
from .file_convertor import FORMATEXP

logger = FormatAdapter(logging.getLogger(__name__))


class Replacer(object):

    def __init__(self, dict_pointer):
        self._messages = {}
        rest, extension = os.path.splitext(dict_pointer)
        dict_path = rest + ".dict"
        if os.path.isfile(dict_path):
            with open(dict_path) as dict_info:
                for line in dict_info:
                    parts = line.strip().split(",", 2)
                    if len(parts) != 3:
                        continue
                    if not parts[0].isdigit():
                        continue
                    self._messages[parts[0]] = parts
        else:
            logger.error(
                "Unable to find a dictionary file at {}".format(dict_path))

    def replace(self, short):
        parts = short.split(" ")
        if not parts[0].isdigit():
            return short  # Not a short format
        if not parts[0] in self._messages:
            return short
        (id, preface, original) = self._messages[parts[0]]
        replaced = original
        if len(parts) > 1:
            matches = FORMATEXP.findall(original)
            if len(matches) != len(parts) - 1:
                # wrong number of elemments so not short after all
                return short
            for i in range(len(matches)):
                replaced = replaced.replace(matches[i], parts[i+1], 1)
        return preface + replaced


if __name__ == '__main__':
    replacer = Replacer()
    replacer.replace()
