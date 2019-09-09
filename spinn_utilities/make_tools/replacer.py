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


def _pop_bytes(parts):
   return struct.pack("!I", int(parts.pop(0), 16))

def pass_through(parts):
    return str(parts.pop(0))


def pass_two(parts):
    return str(parts.pop(0)) + " " + str(parts.pop(0))


def hex_to_float(parts):
    return str(struct.unpack('!f', _pop_bytes(parts))[0])


def hexes_to_double(parts):
    return str(struct.unpack(
        '!d', _pop_bytes(parts) + _pop_bytes(parts))[0])


def hex_to_signed_int(parts):
    return str(struct.unpack('!i', _pop_bytes(parts))[0])


def hex_to_unsigned_int(parts):
    return str(struct.unpack('!I', _pop_bytes(parts))[0])
    #return "signed_int:" + str(struct.pack("!I", int(parts.pop(0), 16)))


CONVERTER = {'a': pass_through,  # float in hexidecimal Specifically 1 word
             # double in hexidecimal Specifically 2 word
             'A': pass_two,
             'c': pass_through,  # character
             'd': hex_to_signed_int,  # signed decimal number.
             'f': hex_to_float,  # float Specifically 1 word
             'F': hexes_to_double,  # double Specifically 2 word
             'i': hex_to_signed_int,  # signed decimal number.
             'k': pass_through,  # ISO signed accum (s1615)
             'K': pass_through,  # ISO unsigned accum (u1616)
             'r': pass_through,  # ISO signed fract (s015)
             'R': pass_through,  # ISO unsigned fract (u016)
             's': pass_through,  # string
             'u': hex_to_unsigned_int,  # decimal unsigned int
             'x': pass_through,  # Fixed point
             }


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
        if short.startswith("13"):
            print(short)
        parts = short.split(TOKEN)
        if not parts[0].isdigit():
            return short
        if not parts[0] in self._messages:
            return short
        (_id, preface, original) = self._messages[parts.pop(0)]
        replaced = six.b(original).decode("unicode_escape")
        if len(parts) > 0:
            matches = FORMAT_EXP.findall(original)
            # Remove any blanks due to double spacing
            matches = [x for x in matches if x != ""]
            try:
                for match in matches:
                    replacement = CONVERTER[match[-1]](parts)
                    replaced = replaced.replace(match, replacement, 1)
            except Exception as ex:
                print(ex)
                return short

        return preface + replaced
