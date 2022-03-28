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
import struct
from spinn_utilities.log import FormatAdapter
from .file_converter import FORMAT_EXP
from .file_converter import TOKEN
from .log_sqllite_database import LogSqlLiteDatabase

logger = FormatAdapter(logging.getLogger(__name__))

LEVELS = {10: "[DEBUG]",
          20: "[INFO]",
          30: "[WARN]",
          40: "[ERROR]"}


class Replacer(LogSqlLiteDatabase):
    """ Performs replacements.
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # nothing yet
        pass

    _INT_FMT = struct.Struct("!I")
    _FLT_FMT = struct.Struct("!f")
    _DBL_FMT = struct.Struct("!d")

    def replace(self, short):
        """ Apply the replacements to a short message.

        :param str short: The short message to apply the transform to.
        :return: The expanded message.
        :rtype: str
        """
        parts = short.split(TOKEN)
        if not parts[0].isdigit():
            return short
        data = self.get_log_info(parts[0])
        if data is None:
            return short
        (log_level, file_name, line_num, original) = data
        preface = f"{LEVELS[log_level]} ({file_name}: {line_num}): "

        replaced = original.encode("latin-1").decode("unicode_escape")
        if len(parts) > 1:
            matches = FORMAT_EXP.findall(original)
            # Remove any blanks due to double spacing
            matches = [x for x in matches if x != ""]
            # Start at 0 so first i+1 puts you at 1 as part 0 is the short
            i = 0
            try:
                for match in matches:
                    i += 1
                    if match.endswith("f"):
                        replacement = str(self._hex_to_float(parts[i]))
                    elif match.endswith("F"):
                        replacement = str(self._hexes_to_double(
                            parts[i], parts[i+1]))
                        i += 1
                    else:
                        replacement = parts[i]
                    replaced = replaced.replace(match, replacement, 1)
            except Exception:  # pylint: disable=broad-except
                return short

        return preface + replaced

    def _hex_to_float(self, hex_str):
        return self._FLT_FMT.unpack(
            self._INT_FMT.pack(int(hex_str, 16)))[0]

    def _hexes_to_double(self, upper, lower):
        return self._DBL_FMT.unpack(
            self._INT_FMT.pack(int(upper, 16)) +
            self._INT_FMT.pack(int(lower, 16)))[0]
