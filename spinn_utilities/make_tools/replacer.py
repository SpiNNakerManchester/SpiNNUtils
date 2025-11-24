# Copyright (c) 2018 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import shutil
import struct
import sys
from types import TracebackType
from typing import Dict, Optional, Type, Tuple

from typing_extensions import Literal, Self

from spinn_utilities.config_holder import get_config_str_or_none
from spinn_utilities.log import FormatAdapter
from spinn_utilities.exceptions import SpiNNUtilsException

from .file_converter import FORMAT_EXP
from .file_converter import TOKEN
from .log_sqllite_database import DB_FILE_NAME, LogSqlLiteDatabase

logger = FormatAdapter(logging.getLogger(__name__))

LEVELS = {10: "[DEBUG]",
          20: "[INFO]",
          30: "[WARN]",
          40: "[ERROR]"}


class Replacer(object):
    """
    Performs replacements.
    """

    __slots__ = []

    # global mapping of
    _dbs: Dict[str, LogSqlLiteDatabase] = dict()
    _paths: Dict[str, str] = dict()

    def _check_default_database_file(self) -> None:
        database_file = LogSqlLiteDatabase.default_database_file()
        if os.path.isfile(database_file):
            return

        external_binaries = get_config_str_or_none(
            "Mapping", "external_binaries")
        if external_binaries is not None:
            source_file = os.path.join(external_binaries, DB_FILE_NAME)
            if os.path.exists(source_file):
                shutil.copyfile(source_file, database_file)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: Optional[Type], exc_val: Exception,
                 exc_tb: TracebackType) -> Literal[False]:
        return False

    _INT_FMT = struct.Struct("!I")
    _FLT_FMT = struct.Struct("!f")
    _DBL_FMT = struct.Struct("!d")

    def _db(self, key: str) -> LogSqlLiteDatabase:
        if key in self._dbs:
            return self._dbs[key]

        key = ""
        if "" not in self._dbs:
            self._dbs[""] = LogSqlLiteDatabase(
                LogSqlLiteDatabase.default_database_file())
        return self._dbs[key]

    @classmethod
    def register_database_path(cls, database_path: str) -> None:
        """
        Adds a database to use to lookup log message.

        The database will be registered using its database keys

        Registering the same path multiple time is fine

        :param database_path: Path to an existing database
        :raises SpiNNUtilsException: If a second path/ database is
            regsitered that uses the same key(s)
        """
        db = LogSqlLiteDatabase(database_path)
        keys = db.get_database_keys()
        for key in keys:
            if key in cls._dbs:
                if cls._paths[key] != database_path:
                    raise SpiNNUtilsException(
                        f"Both {database_path} and "
                        f"{cls._dbs[key]} use the key {key}")
            cls._paths[key] = database_path
            cls._dbs[key] = LogSqlLiteDatabase(database_path)

    @classmethod
    def register_database_dir(cls, database_dir: str) -> None:
        """
        Adds a directory that may contain a logs.sqlite3

        If the database exists it will registered using its database keys

        Registering the same database multiple time sis fine but registering
        two that use the same key(s) will not.

        :param database_dir: Full path to the directory
        """
        database_path = os.path.join(database_dir, DB_FILE_NAME)
        if os.path.exists(database_path):
            cls.register_database_path(database_path)

    def _replace(self, short: str) -> Optional[Tuple[int, str, str, str]]:
        """
        Apply the replacements to a short message.

        :param short: The short message to apply the transform to.
        :return: The expanded message.
        """
        if not short:
            return None
        parts = short.split(TOKEN)
        log_st = parts[0]
        if log_st[0].isdigit():
            log_id = int(log_st)
            database_key = ""
        elif log_st[1:].isdigit():
            log_id = int(log_st[1:])
            database_key = log_st[0]
        else:
            return None

        data = self._db(database_key).get_log_info(log_id)
        if data is None:
            return None

        (log_level, file_name, line_num, original) = data

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
                # If anything goes wrong don't do replace
                return None
        return (log_level, file_name, line_num, replaced)

    def replace(self, short: str) -> str:
        """
        Apply the replacements to a short message.

        :param short: The short string as read of the machine
        :returns: The message as it would if short codes where not used.
        """
        data = self._replace(short)
        if data is None:
            return short
        (log_level, file_name, line_num, replaced) = data
        return f"{LEVELS[log_level]} ({file_name}: {line_num}): {replaced}"

    def _hex_to_float(self, hex_str: str) -> float:
        return self._FLT_FMT.unpack(
            self._INT_FMT.pack(int(hex_str, 16)))[0]

    def _hexes_to_double(self, upper: str, lower: str) -> float:
        return self._DBL_FMT.unpack(
            self._INT_FMT.pack(int(upper, 16)) +
            self._INT_FMT.pack(int(lower, 16)))[0]


if __name__ == '__main__':
    encoded = sys.argv[1]
    LINE = "".join([c if c.isalnum() else TOKEN for c in encoded])
    with Replacer() as replacer:
        print(replacer.replace(LINE))
