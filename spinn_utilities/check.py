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
# from spinn_utilities.overrides import overrides


class Base(object):
    """ The parent """
    def four_params(self, x: int, y: int, z: int) -> List[int]:
        """I have four params including self"""
        return [x, y, z]

    def named_params(self, x: int, *, y: int, z: int) -> List[int]:
        """I have twoe unnamed (including self) and two named params"""
        return [x, y, z]


class TooMany(Base):
    """  param too many"""
    # overrides(Base.four_params)
    def four_params(self, x: int, y: int, z: int, w: int) -> List[int]:
        """1 param too many"""
        return  [x, y, z, w]

    def named_params(self, x: int, *, y: int, z: int, w: int) -> List[int]:
        """1 named param too many"""
        return [x, y, z, w]


class ExtraDefaulted(Base):
    """ Ok to add a param if defaulted """
    # overrides(Base.four_params)
    def four_params(self, x: int, y: int, z: int, w: int = 2) -> List[int]:
        """ Ok to add a param if defaulted """
        return [x, y, z, w]

    def named_params(self, x: int, *, y: int, z: int, w: int = 2) -> List[int]:
        """1 named param too many"""
        return [x, y, z, w]


class TooFew(Base):
    """1 param missing"""
    # overrides(Base.four_params)
    def four_params(self, x: int, z: int) -> List[int]:
        """ 1 param missing"""
        return [x, z]

    def named_params(self, x: int, *, z: int) -> List[int]:
        """ 1 param missing"""
        return [x, z]


class Renamed(Base):
    """ 1 param renamed """
    # overrides(Base.four_params)
    def four_params(self, x: int, p: int, z: int) -> List[int]:
        """ 1 param renamed """
        return [x, p, z]

    def named_params(self, x: int, *, p: int, z: int) -> List[int]:
        """ 1 param renamed """
        return [x, p, z]


# while if all works does not mean we like it
too_many = TooMany()
print(too_many.four_params(1, 2, 3, 4))
print(too_many.named_params(1, y=2, z=3, w=4))

too_many = ExtraDefaulted()
print(too_many.four_params(1, 2, 3, 4))
print(too_many.named_params(1, y=2, z=3, w=4))

too_few = TooFew()
print(too_few.four_params(1, 2))
print(too_few.named_params(1, z=2))

renamed = Renamed()
print(renamed.four_params(1, 2, 3))
print(renamed.named_params(1, p=2, z=3))