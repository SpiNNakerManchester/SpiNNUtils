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


def as_string(bytestring, start=None, end=None):
    """
    Returns the length and the hex values.

    The length is always the full length irrespective of the start and end.

    :param bytestring: data as a bytestring
    :param start: the inclusive start of the slice to return. May be None
    :param end: the exclusive end of the slice to return. May be None
    :return: The length of the bytesting and the hex values, comma separated
    """
    return "(" + str(len(bytestring)) + ")" + as_hex(bytestring, start, end)


def as_hex(bytestring, start=None, end=None):
    """
    Returns the bytestring as string showing the hex values

    :param bytestring: data as a byteString
    :param start: the inclusive start of the slice to return. May be None
    :param end: the exclusive end of the slice to return. May be None
    :return: Comma separated hex values
    """
    return ','.join('%02x' % i for i in iter(bytestring[start:end]))
