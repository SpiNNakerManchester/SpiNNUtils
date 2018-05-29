import logging
import os
from spinn_utilities.log import FormatAdapter
from .file_converter import FORMAT_EXP
from .file_converter import TOKEN

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
            logger.error("Unable to find a dictionary file at {}"
                         .format(dict_path))

    def replace(self, short):
        parts = short.split(TOKEN)
        if not parts[0].isdigit():
            return short
        if not parts[0] in self._messages:
            return short
        (id, preface, original) = self._messages[parts[0]]
        replaced = original
        if len(parts) > 1:
            matches = FORMAT_EXP.findall(original)
            if len(matches) != len(parts) - 1:
                # try removing any blanks due to double spacing
                matches = [x for x in matches if x != ""]
            if len(matches) != len(parts) - 1:
                # wrong number of elemments so not short after all
                return short
            for i in range(len(matches)):
                replaced = replaced.replace(matches[i], parts[i+1], 1)
        return preface + replaced
