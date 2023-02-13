# Copyright (c) 2018-2023 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
