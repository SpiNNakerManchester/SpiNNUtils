# Copyright (c) 2018 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os
import struct
from spinn_utilities.log import FormatAdapter
from .file_converter import FORMAT_EXP
from .file_converter import TOKEN
import six

logger = FormatAdapter(logging.getLogger(__name__))


class Replacer(object):

    def __init__(self, dict_pointer):
        self._messages = {}
        rest, _ = os.path.splitext(dict_pointer)
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
        (_id, preface, original) = self._messages[parts[0]]
        replaced = six.b(original).decode("unicode_escape")
        if len(parts) > 1:
            matches = FORMAT_EXP.findall(original)
            if len(matches) != len(parts) - 1:
                # try removing any blanks due to double spacing
                matches = [x for x in matches if x != ""]
            if len(matches) != len(parts) - 1:
                # wrong number of elements so not short after all
                return short
            for i, match in enumerate(matches):
                if match == "%f":
                    print(match, original)
                    replacement = str(self.hex_to_float(parts[i + 1]))
                else:
                    replacement = parts[i + 1]
                replaced = replaced.replace(match, replacement, 1)
        return preface + replaced

    def hex_to_float(self, hex):
        print(hex)
        return struct.unpack('!f', struct.pack("!I", int(hex, 16)))[0]
