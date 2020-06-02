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

import os

alternative_path = None


def find_dict():
    if alternative_path is not None:
        return alternative_path

    spin_dirs = os.environ.get('SPINN_DIRS', None)
    if spin_dirs is None:
        raise Exception("Environment variable SPINN_DIRS MUST be set")
    if not os.path.exists(spin_dirs):
        raise Exception(
            "Unable to locate spin_dirs directory {}".format(spin_dirs))
    return os.path.join(spin_dirs, "logs.dict")


def set_alternative_dict_path(new_path):
    global alternative_path
    new_logs = os.path.join(new_path, "logs.dict")
    if os.path.exists(new_logs):
        alternative_path = new_logs
