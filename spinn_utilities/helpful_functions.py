# Copyright (c) 2017 The University of Manchester
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

from functools import reduce
import logging
import math
from spinn_utilities.log import FormatAdapter


logger = FormatAdapter(logging.getLogger(__name__))
FINISHED_FILENAME = "finished"


def is_singleton(value):
    """
    Tests whether the value is a singleton.

    Singleton types are strings and any other class that can not be
    iterated.

    Strings are considered singleton as only rarely will someone use a string
    to represent an iterable of characters.
    """
    return not hasattr(value, '__iter__') or isinstance(value, str)


def _lcm(a, b):
    return (a * b) // math.gcd(a, b)


def lcm(*numbers):
    """
    Lowest common multiple of 0, 1 or more integers.

    GIGO: If any of the values are anything except positive `int` values
    this function will either produce incorrect results or raise an exception.

    :param numbers: The Positive integers to get the LCM for.
        This can be zero, one or more int values or
        a singleton which is an iterator (possibly empty) of `int`\\s.
    :return: the LCM, or 1 if `numbers` is empty or an empty iterator
    :rtype: int
    :raises TypeError: If any value cannot be interpreted as an integer
    :raises ZeroDivisionError: May be raised if one of the values is zero
    """
    if len(numbers) == 1:
        try:
            return reduce(_lcm, iter(numbers[0]), 1)
        except TypeError:
            return numbers[0]
    return reduce(_lcm, numbers, 1)


def gcd(*numbers):
    """
    Greatest common divisor of 1 or more integers.

    GIGO: If any of the values are anything except positive `int` values
    this function will either produce incorrect results or raise an exception.

    :param numbers: The positive integers to get the GCD for.
        This can be one or more `int` values or
        a singleton which is an iterator (*not* empty) of `int`\\s.
    :return: the GCD
    :rtype: int
    :raises TypeError: If any value cannot be interpreted as an integer or
        if no values are provided
    :raises ZeroDivisionError: May be raised if one of the values is zero
    """
    if len(numbers) == 1:
        try:
            return reduce(math.gcd, iter(numbers[0]))
        except TypeError:
            return numbers[0]
    return reduce(math.gcd, numbers)
