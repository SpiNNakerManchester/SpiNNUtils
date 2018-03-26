import os

from .convertor import FORMATEXP


class Replacer(object):

    def __init__(self, convertor_dir=None):
        self._messages = {}
        if convertor_dir is None:
            convertor_dir = os.path.dirname(os.path.abspath(__file__))
        all_files = os.listdir(convertor_dir)
        for csv_file in all_files:
            if not csv_file.endswith(".csv"):
                continue
            path = os.path.join(convertor_dir, csv_file)
            with open(path) as csv_info:
                for line in csv_info:
                    parts = line.split(",", 2)
                    if len(parts) != 3:
                        continue
                    if not parts[0].isdigit():
                        continue
                    self._messages[parts[0]] = parts

    def replace(self, short):
        parts = short.split(" ")
        if not parts[0].isdigit():
            return short  # Not a short format
        if not parts[0] in self._messages:
            return short
        (id, preface, original) = self._messages[parts[0]]
        if len(parts) > 1:
            matches = FORMATEXP.findall(original)
            if len(matches) != len(parts) - 1:
                return short  # wrong number of elemments so not short after all
            for match in matches:
                return match.group(0)
        else:
            replaced = original
        return preface + replaced


if __name__ == '__main__':
    replacer = Replacer()
    replacer.replace()
