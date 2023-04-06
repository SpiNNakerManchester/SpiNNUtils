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


def as_string(byte_string, start=None, end=None):
    """
    Returns the length and the hex values.

    The length is always the full length irrespective of the start and end.

    :param bytes byte_string: data as a byte string
    :param int start:
        The inclusive start of the slice to convert to hexadecimal.
        May be `None`
    :param int end:
        The exclusive end of the slice to convert to hexadecimal. May be `None`
    :return:
        The length of the byte string and the comma separated hex values, as a
        descriptive string
    :rtype: str
    """
    return "(" + str(len(byte_string)) + ")" + as_hex(byte_string, start, end)


def as_hex(byte_string, start=None, end=None):
    """
    Returns the byte string as string showing the hex values

    :param bytes byte_string: data as a byte string
    :param int start: the inclusive start of the slice to return. May be `None`
    :param int end: the exclusive end of the slice to return. May be `None`
    :return: Comma-separated hex values
    :rtype: str
    """
    return ','.join('%02x' % i for i in iter(byte_string[start:end]))
