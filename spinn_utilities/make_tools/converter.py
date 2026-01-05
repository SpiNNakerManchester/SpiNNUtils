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

import os
import sys
from .file_converter import FileConverter
from .log_sqllite_database import LogSqlLiteDatabase

ALLOWED_EXTENSIONS = frozenset([".c", ".cpp", ".h"])
SKIPPABLE_FILES = frozenset([
    "common.mk", "Makefile.common",
    "paths.mk", "Makefile.paths",
    "neural_build.mk", "Makefile.neural_build"])


def convert(src: str, dest: str, database_dir: str,
            database_key: str) -> str:
    """
    Converts a whole directory including sub-directories.

    :param src: Full source directory
    :param dest: Full destination directory
    :param database_dir:
        Full path to directory to place database file in.
    :param database_key: database key for this conversion
    :return: Full path to the logs database
    :raises ValueError:
    """
    database_file =LogSqlLiteDatabase.filename_by_key(
        database_dir, database_key)
    log_database = LogSqlLiteDatabase(database_file, read_only=False)

    src_path = os.path.abspath(src)
    if not os.path.exists(src_path):
        raise FileNotFoundError(
            f"Unable to locate source directory {src_path}")
    dest_path = os.path.abspath(dest)
    file_converter = FileConverter(log_database, database_key)
    _convert_dir(src_path, dest_path, file_converter)
    return database_file


def _convert_dir(src_path: str, dest_path: str,
                 file_converter: FileConverter) -> None:
    """
    Converts a whole directory including sub directories.

    :param src_path: Full source directory
    :param dest_path: Full destination directory
    :param file_converter:
    """
    for src_dir, _, file_list in os.walk(src_path):
        dest_dir = os.path.join(dest_path, os.path.relpath(src_dir, src_path))
        for file_name in file_list:
            _, extension = os.path.splitext(file_name)
            if extension in ALLOWED_EXTENSIONS:
                file_converter.convert(src_dir, dest_dir, file_name)
            elif file_name in SKIPPABLE_FILES:
                pass
            else:
                source = os.path.join(src_dir, file_name)
                print(f"Unexpected file {source}")


def _mkdir(destination: str) -> None:
    if not os.path.exists(destination):
        os.mkdir(destination)
    if not os.path.exists(destination):
        raise FileNotFoundError(f"mkdir failed {destination}")


if __name__ == '__main__':
    _src = sys.argv[1]
    _dest = sys.argv[2]
    if len(sys.argv) > 4:
        _database_file = sys.argv[3]
        _database_key = sys.argv[4]
        convert(_src, _dest, _database_file, _database_key)
    else:
        raise ValueError(
            "Convert requires 4 parameters. The source directory, "
            "the destination directory, a single character database key and "
            "the path to write the logs.sqlite3 database to. "
            "Database keys must be unique. "
            "To avoid clashes with system builds use a lower case letter")
