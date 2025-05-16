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

from typing import List
from spinn_utilities.overrides import overrides


class Base(object):
    def four_params(self, x: int, y: int, z: int) -> List[int]:
        """I have four params including self"""
        return [x, y, z]


class TooMany(Base):
    @overrides(Base.four_params)
    def four_params(self, x: int, y: int, z: int, w: int) -> List[int]:
        """ Oops 1 param too many"""
        return [w, z, y, x]


class TooFew(Base):
    @overrides(Base.four_params)
    def four_params(self, x: int, y: int, z: int, w: int) -> List[int]:
        """ Oops 1 param missing"""
        return [w, z, y, x]


class Renamed(Base):
    @overrides(Base.four_params)
    def four_params(self, x: int, p: int, z: int) -> List[int]:
        """ Oops 1 param missing"""
        return [x, p, z]
