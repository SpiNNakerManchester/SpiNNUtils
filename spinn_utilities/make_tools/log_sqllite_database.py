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
from typing import Dict, Optional, Tuple
from spinn_utilities.abstract_context_manager import AbstractContextManager

_DDL_FILE = os.path.join(os.path.dirname(__file__), "db.sql")
_SECONDS_TO_MICRO_SECONDS_CONVERSION = 1000
DB_FILE_NAME = "logs.sqlite3"


def _timestamp() -> int:
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

    def __init__(self, database_path: str) -> None:
        """
        Connects to a log dict. The location of the file can be overridden
        using the ``C_LOGS_DICT`` environment variable.

        param database_file: Full path to the database.
           (use default_database_file to get the default location)
        """
        # To Avoid an Attribute error on close after an exception
        self._db: Optional[sqlite3.Connection] = None
        self._db = sqlite3.connect(database_path)
        self.__init_db()

    @classmethod
    def default_database_file(cls) -> str:
        """
        Finds the previous database file path.

        If environment variable C_LOGS_DICT exists that is used,
        otherwise the default path in this directory is used.

        This is deprecated as any new make will no longer use this file

        :return: Absolute path to where the database file is or will be
        """
        if 'C_LOGS_DICT' in os.environ:
            return str(os.environ['C_LOGS_DICT'])

        script = sys.modules[cls.__module__].__file__
        assert script is not None
        directory = os.path.dirname(script)
        return os.path.join(directory, DB_FILE_NAME)

    def _check_database_file(self, database_file: str) -> None:
        """
        Checks the database file exists:

        :param database_file: Absolute path to the database file
        :raises FileNotFoundErrorL If the file does not exists
        """
        if os.path.exists(database_file):
            return
        message = f"Unable to locate c_logs_dict at {database_file}. "
        if 'C_LOGS_DICT' in os.environ:
            message += (
                "This came from the environment variable 'C_LOGS_DICT'. ")
        message += "Please rebuild the C code."
        raise FileNotFoundError(message)

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        """
        Finalises and closes the database.
        """
        try:
            if self._db is not None:
                self._db.close()
        except Exception as ex:  # pylint: disable=broad-except
            print(ex)
        self._db = None

    def __init_db(self) -> None:
        """
        Set up the database if required.
        """
        assert self._db is not None
        self._db.row_factory = sqlite3.Row
        # Don't use memoryview / buffer as hard to deal with difference
        self._db.text_factory = str
        with open(_DDL_FILE, encoding="utf-8") as f:
            sql = f.read()
        self._db.executescript(sql)

    def get_directory_id(self, src_path: str, dest_path: str) -> int:
        """
        gets the Ids for this directory. Making a new one if needed

        :param src_path:
        :param dest_path:
        :returns: The ID for this directory.
        """
        assert self._db is not None
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
            directory_id = cursor.lastrowid
            assert directory_id is not None
            return directory_id

    def get_file_id(self, directory_id: int, file_name: str) -> int:
        """
        Gets the id for this file, making a new one if needed.

        :param directory_id:
        :param file_name:
        :returns: The ID for this file
        """
        assert self._db is not None
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
                file_id = cursor.lastrowid
                assert file_id is not None
                return file_id

    def set_log_info(self, log_level: int, line_num: int,
                     original: str, file_id: int) -> int:
        """
        Saves the data needed to replace a short log back to the original.

        :param log_level:
        :param line_num:
        :param original:
        :param file_id:
        :returns: ID for this log message
        """
        assert self._db is not None
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
                log_id = cursor.lastrowid
                assert log_id is not None
                return log_id
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
        raise ValueError("unexpected no return")

    def get_log_info(self, log_id: str) -> Optional[Tuple[int, str, str, str]]:
        """
        Gets the data needed to replace a short log back to the original.

        :param log_id: The int id as a String
        :returns: log level, file name, line number and the original text
        """
        assert self._db is not None
        with self._db:
            for row in self._db.execute(
                    """
                    SELECT log_level, file_name, line_num , original,
                            last_build
                    FROM replacer_view
                    WHERE log_id = ?
                    LIMIT 1
                    """, [log_id]):
                if row["last_build"]:
                    line_number = str(row["line_num"])
                else:
                    line_number = str(row["line_num"]) + "*"
                return (row["log_level"], row["file_name"], line_number,
                        row["original"])
        return None

    def check_original(self, original: str) -> None:
        """
        Checks that an original log line has been added to the database.

        Mainly used for testing

        :param original:
        :raises ValueError: If the original is not in the database
        """
        assert self._db is not None
        with self._db:
            for row in self._db.execute(
                    """
                    SELECT COUNT(log_id) as "counts"
                    FROM log
                    WHERE original = ?
                    """, ([original])):
                if row["counts"] == 0:
                    raise ValueError(f"{original} not found in database")

    def get_max_log_id(self) -> Optional[int]:
        """
        :returns: the max id of any log message, or None it there  none
        """
        assert self._db is not None
        with self._db:
            for row in self._db.execute(
                    """
                    SELECT MAX(log_id) AS "max_id"
                    FROM log
                     """):
                return row["max_id"]
        raise ValueError("unexpected no return")

    def set_database_key(self, new_key: str) -> None:
        """
        Sets/ adds a new database key to the database.

        A database may have more than 1 key

        :param new_key: An empty or single char key
        """
        assert self._db is not None
        with self._db:
            cursor = self._db.cursor()
            cursor.execute(
                """
                INSERT OR IGNORE INTO database_keys( database_key)
                VALUES(?)
                """, (new_key,))

    @classmethod
    def filename_by_key(cls, database_dir: str, database_key: str) -> str:
        """
        Builds the file name which includes the key

        :param database_dir:
            Full path to directory to place database file in.
        :param database_key: key for the database
        :return: filename including the key
        :raises ValueError: If the key is not a single none digital character
        """
        if len(database_key) != 1:
            raise ValueError(f"{database_key=} Only single character allowed")
        if database_key.isdigit():
            raise ValueError(f"{database_key=} is digital")

        return os.path.join(database_dir, f"logs{database_key}.sqlite3")

    @classmethod
    def key_from_filename(cls, file_path: str) -> str:
        """
        Gets the key from the excepted filename pattern logs{key}.sqlite3

        :param file_path: full path or filename in the pattern logs{key}.sqlite3
        :return: database key
        """
        try:
            database_key = file_path[-9]
        except IndexError as exc:
            msg = (f"Unexpected Database {file_path}. "
                   "It should be logs{key}.sqlite3")
            raise ValueError(msg) from exc
        check = cls.filename_by_key(os.path.dirname(file_path), database_key)
        if check != file_path:
            msg = (f"Unexpected Database {file_path}. "
                   "Only logs{key}.sqlite3 expected")
            raise ValueError(msg)
        return database_key

    @classmethod
    def find_databases(cls, database_dir: str) -> Dict[str, str]:
        """
        Given a directory finds the databases and keys in it.

        :param database_dir:
            Full path to directory which may have logs databases) in it.
        :return: Map of database_keys to full database paths.
        """
        logfiles: Dict[str, str] = dict()
        for file in os.listdir(database_dir):
            if file.endswith(".sqlite3"):
                filepath = os.path.join(database_dir, file)
                logfiles[cls.key_from_filename(filepath)] = filepath
        return logfiles
