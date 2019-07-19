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

import logging
import inspect
import re
from six import string_types

logger = logging.getLogger(__name__)
FINISHED_FILENAME = "finished"


def get_valid_components(module, terminator):
    """ Get possible components, stripping the given suffix from their\
        class names.

    :param module: The module containing the classes to obtain.
    :param terminator: \
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
    return not hasattr(value, '__iter__') or isinstance(value, string_types)
