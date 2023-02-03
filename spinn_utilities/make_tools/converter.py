# Copyright (c) 2018-2019 The University of Manchester
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
import sys
from .file_converter import FileConverter
from .log_sqllite_database import LogSqlLiteDatabase

SKIPPABLE_FILES = ["common.mk", "Makefile.common",
                   "paths.mk", "Makefile.paths",
                   "neural_build.mk", "Makefile.neural_build"]


def convert(src, dest, new_dict):
    """ Converts a whole directory including sub directories

    :param str src: Full source directory
    :param str dest: Full destination directory
    :param bool new_dict: says if we should generate a new dict
    """
    if new_dict:
        LogSqlLiteDatabase(new_dict)

    src_path = os.path.abspath(src)
    if not os.path.exists(src_path):
        raise FileNotFoundError(
            f"Unable to locate source directory {src_path}")
    dest_path = os.path.abspath(dest)
    __convert_dir(src_path, dest_path)


def __convert_dir(src_path, dest_path):
    """ Converts a whole directory including sub directories

    :param str src_path: Full source directory
    :param str dest_path: Full destination directory
    """
#    __mkdir(dest_path)
    for src_dir, _, file_list in os.walk(src_path):
        dest_dir = os.path.join(dest_path, os.path.relpath(src_dir, src_path))
#        __mkdir(dest_dir)
        for file_name in file_list:
            _, extension = os.path.splitext(file_name)
            if extension in [".c", ".cpp", ".h"]:
                FileConverter.convert(src_dir, dest_dir, file_name)
            elif file_name in SKIPPABLE_FILES:
                pass
            else:
                source = os.path.join(src_dir, file_name)
                print("Unexpected file {}".format(source))


def __mkdir(destination):
    if not os.path.exists(destination):
        os.mkdir(destination)
    if not os.path.exists(destination):
        raise FileNotFoundError("mkdir failed {}".format(destination))


if __name__ == '__main__':
    _src = sys.argv[1]
    _dest = sys.argv[2]
    if len(sys.argv) > 3:
        _new_dict = bool(sys.argv[3])
    else:
        _new_dict = False
    convert(_src, _dest, _new_dict)
