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
from typing import Optional
from .file_converter import FileConverter
from .log_sqllite_database import LogSqlLiteDatabase

ALLOWED_EXTENSIONS = frozenset([".c", ".cpp", ".h"])
SKIPPABLE_FILES = frozenset([
    "common.mk", "Makefile.common",
    "paths.mk", "Makefile.paths",
    "neural_build.mk", "Makefile.neural_build"])


def convert(src: str, dest: str, database_key: Optional[str] = None,
            database_path: Optional[str] = None) -> None:
    """
    Converts a whole directory including sub-directories.

    :param src: Full source directory
    :param dest: Full destination directory
    :param database_key: Key to the specific database to use.
        None or "" for default databae or a non digital char.
    :param database_path: Path to the log database.
        Required if database_key specifed, otherwise ignored
    """
    src_path = os.path.abspath(src)
    if not os.path.exists(src_path):
        raise FileNotFoundError(
            f"Unable to locate source directory {src_path}")
    dest_path = os.path.abspath(dest)
    _convert_dir(src_path, dest_path, database_key, database_path)


def _convert_dir(src_path: str, dest_path: str, database_key: int,
                 database_path: str) -> None:
    """
    Converts a whole directory including sub directories.

    :param src_path: Full source directory
    :param dest_path: Full destination directory
    :param database_path: Path to the log database.
        Required if database_key specifed, otherwise ignored
    :param database_path: Path to the log database.
        Required if database_key specifed, otherwise ignored
    """
    for src_dir, _, file_list in os.walk(src_path):
        dest_dir = os.path.join(dest_path, os.path.relpath(src_dir, src_path))
        #if make_directories:
        #    _mkdir(dest_dir)
        for file_name in file_list:
            _, extension = os.path.splitext(file_name)
            if extension in ALLOWED_EXTENSIONS:
                FileConverter.convert(
                    src_dir, dest_dir, file_name, database_key, database_path)
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
    src = sys.argv[1]
    dest = sys.argv[2]
    if len(sys.argv) < 5:
        convert(src, dest)
    else:
        database_key = sys.argv[3]
        database_path = sys.argv[4]
        convert(src, dest, database_key, database_path)
