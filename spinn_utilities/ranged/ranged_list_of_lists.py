# Copyright (c) 2021 The University of Manchester
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

from spinn_utilities.helpful_functions import is_singleton
from spinn_utilities.overrides import overrides
from .ranged_list import RangedList


class RangedListOfList(RangedList):

    # pylint: disable=unused-argument
    @staticmethod
    @overrides(RangedList.is_list)
    def is_list(value, size):  # @UnusedVariable
        if callable(value):
            return True
        if is_singleton(value):
            raise TypeError(
                "Value must be an iterable or iterable of iterables")
        try:
            # Must be an iterable
            if len(value) == 0:
                return False
            # All or No values must be singletons
            singleton = is_singleton(value[0])
            for i in range(1, len(value)):
                if singleton != is_singleton(value[i]):
                    raise ValueError(
                        "Illegal mixing of singleton and iterable")
            # A list of all singletons is a single value not a list here!
            return not singleton
        except TypeError as original:
            raise TypeError(
                "Value must be an iterable or iterable of iterables") \
                from original
