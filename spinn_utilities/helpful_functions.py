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

from functools import reduce
import logging
import inspect
import math
import os
import re
from spinn_utilities.log import FormatAdapter


logger = FormatAdapter(logging.getLogger(__name__))
FINISHED_FILENAME = "finished"


def get_valid_components(module, terminator):
    """ Get possible components, stripping the given suffix from their\
        class names.

    :param module: The module containing the classes to obtain.
    :param str terminator:
        Regular expression string to match the suffix. Anchoring not required.
    :return: mapping from (shortened) name to class
    :rtype: dict(str -> class)
    """
    terminator_re = re.compile(terminator + '$')
    return {terminator_re.sub('', name): router
            for name, router in inspect.getmembers(module, inspect.isclass)}


def is_singleton(value):
    """ Tests whether the value is a singleton.

        Singleton types are strings and any other class that can not be
        iterated.

        Strings are considered singleton as rarely will someone use a String
        to represent an iterable of characters
    """
    return not hasattr(value, '__iter__') or isinstance(value, str)


def _lcm(a, b):
    return (a * b) // math.gcd(a, b)


def lcm(*numbers):
    """
    Lowest common multiple of 0, 1 or more integers.

    GIGO: If any of the values are anything except positive int values
    this function will either produce incorrect results or raise an exception.

    :param numbers: The Positive integers to get the lcm for.
        This can be zero, one or more int values or
        a singleton which is an iterator (possibly empty) of ints.
    :return: the lcm or 1 if numbers is empty or an empty iterator
    :rtype: int
    :raises TypeError: If any value can not be interpreted as an Integer
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

    GIGO: If any of the values are anything except positive int values
    this function will either produce incorrect results or raise an exception.

    :param numbers: The Positive integers to get the GCD for.
        This can be one or more int values or
        a singleton which is an iterator (not empty) of ints.
    :return: the gcd or 1 if numbers is empty or an empty iterator
    :rtype: int
    :raises TypeError: If any value can not be interpreted as an Integer or
        if no values are provided
    :raises ZeroDivisionError: May be raised if one of the values is zero
    """
    if len(numbers) == 1:
        try:
            return reduce(math.gcd, iter(numbers[0]))
        except TypeError:
            return numbers[0]
    return reduce(math.gcd, numbers)
