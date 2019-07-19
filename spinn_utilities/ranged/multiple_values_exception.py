# Copyright (c) 2017-2018 The University of Manchester
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


class MultipleValuesException(Exception):

    def __init__(self, key=None, value1=None, value2=None):
        if key is None:
            msg = "Multiple values found"
        else:
            msg = "Multiple values found for key {}".format(key)
        if value1 is not None and value2 is not None:
            msg += " values found include {} and {}".format(value1, value2)
        super(MultipleValuesException, self).__init__(msg)
