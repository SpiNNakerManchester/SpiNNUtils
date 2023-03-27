# Copyright (c) 2017 The University of Manchester
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

import os
import sqlite3
import sys
import time
from spinn_utilities.abstract_context_manager import AbstractContextManager

_DDL_FILE = os.path.join(os.path.dirname(__file__), "db.sql")
_SECONDS_TO_MICRO_SECONDS_CONVERSION = 1000
DB_FILE_NAME = "logs.sqlite3"


def _timestamp():
    return int(time.time() * _SECONDS_TO_MICRO_SECONDS_CONVERSION)


class LogSqlLiteDatabase(AbstractContextManager):
    """
    Specific implementation of the Database for SQLite 3.

    .. note::
        **Not thread-safe on the same database.**
        Threads can access different DBs just fine.

    .. note::
        This totally relies on the way SQLite's type affinities function.
        You can't port to a different database engine without a lot of work.
    """

    __slots__ = [
        # the database holding the data to store
        "_db",
    ]

    def __init__(self, new_dict=False):
        """
        Connects to a log dict. The location of the file can be overridden
        using the ``C_LOGS_DICT`` environment variable.

        :param bool new_dict: Flag to say if this is a new dict or not.
            If True, clears and previous values.
            If False, makes sure the dict exists.
        """
        # To Avoid an Attribute error on close after an exception
        self._db = None
        database_file = os.environ.get('C_LOGS_DICT', None)
        if database_file is None:
            script = sys.modules[self.__module__].__file__
            directory = os.path.dirname(script)
            database_file = os.path.join(directory, DB_FILE_NAME)

        if not new_dict and not os.path.exists(database_file):
            message = f"Unable to locate c_logs_dict at {database_file}. "
            if 'C_LOGS_DICT' in os.environ:
                message += (
                    "This came from the environment variable 'C_LOGS_DICT'. ")
            message += "Please rebuild the C code."
            raise FileNotFoundError(message)

        try:
            self._db = sqlite3.connect(database_file)
            self.__init_db()
            if new_dict:
                self.__clear_db()
        except Exception as ex:
            message = f"Error accessing c_logs_dict at {database_file}. "
            if 'C_LOGS_DICT' in os.environ:
                message += (
                    "This came from the environment variable 'C_LOGS_DICT'. ")
            else:
                message += (
                    "This is the default location. Set environment "
                    "variable 'C_LOGS_DICT' to use somewhere else.")
            if new_dict:
                message += "Check this is a location with write access."
            else:
                message += "Please rebuild the C code."
            raise FileNotFoundError(message) from ex

    def __del__(self):
        self.close()

    def close(self):
        """
        Finalises and closes the database.
        """
        try:
            if self._db is not None:
                self._db.close()
        except Exception:  # pylint: disable=broad-except
            pass
        self._db = None

    def __init_db(self):
        """
        Set up the database if required.
        """
        self._db.row_factory = sqlite3.Row
        # Don't use memoryview / buffer as hard to deal with difference
        self._db.text_factory = str
        with open(_DDL_FILE, encoding="utf-8") as f:
            sql = f.read()
        self._db.executescript(sql)

    def __clear_db(self):
        with self._db:
            cursor = self._db.cursor()
            cursor.execute("DELETE FROM log")
            cursor.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='log'")
            cursor.execute("DELETE FROM file")
            cursor.execute(
                "UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='file'")
            cursor.execute("DELETE FROM directory")
            cursor.execute(
                "UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='directory'")

    def get_directory_id(self, src_path, dest_path):
        with self._db:
            cursor = self._db.cursor()
            # reuse the existing if it exists
            for row in self._db.execute(
                    """
                    SELECT directory_id
                    FROM directory
                    WHERE src_path = ? AND dest_path = ?
                    LIMIT 1
                    """, [src_path, dest_path]):
                return row["directory_id"]

            # create a new number
            cursor.execute(
                """
                INSERT INTO directory(src_path, dest_path)
                VALUES(?, ?)
                """, (src_path, dest_path))
            return cursor.lastrowid

    def get_file_id(self, directory_id, file_name):
        with self._db:
            # Make previous one as not last
            with self._db:
                cursor = self._db.cursor()
                cursor.execute(
                    """
                    UPDATE file SET last_build = 0
                    WHERE directory_id = ? AND file_name = ?
                    """, [directory_id, file_name])
                # always create new one to distinguish new from old logs
                cursor.execute(
                    """
                    INSERT INTO file(
                        directory_id, file_name, convert_time, last_build)
                    VALUES(?, ?, ?, 1)
                    """, (directory_id, file_name, _timestamp()))
                return cursor.lastrowid

    def set_log_info(self, log_level, line_num, original, file_id):
        with self._db:
            cursor = self._db.cursor()
            # reuse the existing number if nothing has changed
            cursor.execute(
                """
                UPDATE log SET
                    file_id = ?
                WHERE log_level = ? AND line_num = ? AND original = ?
                """, (file_id, log_level, line_num, original))

            if cursor.rowcount == 0:
                # create a new number if anything has changed
                cursor.execute(
                    """
                    INSERT INTO log(log_level, line_num, original, file_id)
                    VALUES(?, ?, ?, ?)
                    """, (log_level, line_num, original, file_id))
                return cursor.lastrowid
            else:
                for row in self._db.execute(
                        """
                        SELECT log_id
                        FROM log
                        WHERE log_level = ? AND line_num = ?
                            AND original = ? AND file_id = ?
                        LIMIT 1
                        """, (log_level, line_num, original, file_id)):
                    return row["log_id"]

    def get_log_info(self, log_id):
        with self._db:
            for row in self._db.execute(
                    """
                    SELECT log_level, file_name, line_num , original
                    FROM current_file_view
                    WHERE log_id = ?
                    LIMIT 1
                    """, [log_id]):
                return (row["log_level"], row["file_name"], row["line_num"],
                        row["original"])

    def check_original(self, original):
        with self._db:
            for row in self._db.execute(
                    """
                    SELECT COUNT(log_id) as "counts"
                    FROM log
                    WHERE original = ?
                    """, ([original])):
                if row["counts"] == 0:
                    raise ValueError(f"{original} not found in database")

    def get_max_log_id(self):
        with self._db:
            for row in self._db.execute(
                    """
                    SELECT MAX(log_id) AS "max_id"
                    FROM log
                     """):
                return row["max_id"]
