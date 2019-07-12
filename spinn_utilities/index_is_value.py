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

import sys


class IndexIsValue(object):
    """ Tiny support class that implements ``object[x]`` by just returning\
        ``x`` itself.

    Used for where you want a range from 1 to *N* but you don't know *N*.

    Clearly, operations that assume a finite list are *not* supported.
    """

    def __getitem__(self, key):
        return key

    def __len__(self):
        return sys.maxsize
