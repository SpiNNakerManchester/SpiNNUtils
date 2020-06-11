# Copyright (c) 2017-2019 The University of Manchester
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

import os
import sqlite3
import time

_DDL_FILE = os.path.join(os.path.dirname(__file__), "db.sql")
_SECONDS_TO_MICRO_SECONDS_CONVERSION = 1000
DB_FILE_NAME = "logs.sqlite3"

database_file = None

def _timestamp():
    return int(time.time() * _SECONDS_TO_MICRO_SECONDS_CONVERSION)

class LogSqlLiteDatabase(object):
    """ Specific implementation of the Database for SQLite 3.

    .. note::
        NOT THREAD SAFE ON THE SAME DB.
        Threads can access different DBs just fine.

    .. note::
        This totally relies on the way SQLite's type affinities function.
        You can't port to a different database engine without a lot of work.
    """

    __slots__ = [
        # the database holding the data to store
        "_db",
    ]

    def __init__(self):
        """
        """
        global database_file
        if database_file is None:
            spin_dirs = os.environ.get('SPINN_DIRS', None)
            if spin_dirs is None:
                raise Exception("Environment variable SPINN_DIRS MUST be set")
            if not os.path.exists(spin_dirs):
                raise Exception(
                    "Unable to locate spin_dirs directory {}".format(spin_dirs))
            database_file = os.path.join(spin_dirs, DB_FILE_NAME)

        self._db = sqlite3.connect(database_file)
        self.__init_db()

    def __del__(self):
        self.close()

    def __enter__(self):
        """ Start method is use in a ``with`` statement
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ End method if used in a ``with`` statement.

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self.close()

    def close(self):
        """ Finalises and closes the database.
        """
        if self._db is not None:
            self._db.close()
            self._db = None

    def __init_db(self):
        """ Set up the database if required.
        """
        self._db.row_factory = sqlite3.Row
        # Don't use memoryview / buffer as hard to deal with difference
        self._db.text_factory = str
        with open(_DDL_FILE) as f:
            sql = f.read()
        self._db.executescript(sql)

    def clear(self):
        with self._db:
            cursor = self._db.cursor()
            cursor.execute("DELETE FROM log")
            cursor.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='log'")
            cursor.execute("DELETE FROM file")
            cursor.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='file'")

    def get_file_id(self, src_path, dest_path):
        with self._db:
            # Make previous one as not last
            with self._db:
                cursor = self._db.cursor()
                cursor.execute(
                    """
                    UPDATE file SET last_build = 0
                    WHERE dest_path = ?
                    """, [dest_path])
                # always create new one to distinguish new from old logs
                cursor.execute(
                """
                INSERT INTO file(src_path, dest_path, convert_time, last_build)
                VALUES(?, ?, ?, 1)
                """, (src_path, dest_path, _timestamp()))
                return cursor.lastrowid

    def set_log_info(self, preface, original, file_id):
        with self._db:
            cursor = self._db.cursor()
            # reuse the existing number if nothing has changed
            cursor.execute(
                """
                UPDATE log SET
                    file_id = ?
                WHERE preface = ? AND original = ?
                """, (file_id, preface, original))

            if cursor.rowcount == 0:
                # create a new number if anything has changed
                cursor.execute(
                    """
                    INSERT INTO log(preface, original, file_id)
                    VALUES(?, ?, ?)
                    """, (preface, original, file_id))
                return cursor.lastrowid
            else:
                for row in self._db.execute(
                        """
                        SELECT log_id
                        FROM log
                        WHERE preface = ? AND original = ? AND file_id = ?
                        LIMIT 1
                        """, (preface, original, file_id)):
                    return row["log_id"]

    def get_log_info(self, log_id):
        with self._db:
            for row in self._db.execute(
                    """
                    SELECT preface, original
                    FROM log
                    WHERE log_id = ?
                    LIMIT 1
                    """, [log_id]):
                return row["preface"], row["original"]

    def check_original(self, original):
        with self._db:
            for row in self._db.execute(
                    """
                    SELECT COUNT(log_id) as "counts"
                    FROM log
                    WHERE original = ?
                    """, ([original])):
                if row["counts"] == 0:
                    raise Exception("Not found")

    def get_max_log_id(self):
        with self._db:
            for row in self._db.execute(
                    """
                    SELECT MAX(log_id) AS "max_id"
                    FROM log
                     """):
                return row["max_id"]

def set_alternative_log_path(new_path):
    global database_file
    new_logs = os.path.join(new_path, DB_FILE_NAME)
    if os.path.exists(new_logs):
        database_file = new_logs
