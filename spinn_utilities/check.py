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
        """I have two unnamed (including self) and two named params"""
        return [x, y, z]

    def defaulted_param(self, x: int, y: int = 2, z: int = 3) -> List[int]:
        """ I have one defaulted param"""
        return [x, y, z]


class TooMany(Base):
    """  param too many"""
    # overrides(Base.four_params)
    def four_params(self, x: int, y: int, z: int, w: int) -> List[int]:
        """
        1 param too many

        arguments-differ
        """
        return [x, y, z, w]

    def named_params(self, x: int, *, y: int, z: int, w: int) -> List[int]:
        """
        1 named param too many

        arguments-differ
        """
        return [x, y, z, w]


class ExtraDefaulted(Base):
    """ OK to add a param if defaulted """
    # overrides(Base.four_params)
    def four_params(self, x: int, y: int, z: int, w: int = 2) -> List[int]:
        """
        OK to add a param if defaulted

        No pylint error
        """
        return [x, y, z, w]

    def named_params(self, x: int, *, y: int, z: int, w: int = 2) -> List[int]:
        """
        1 named param too many

        No pylint error
        """
        return [x, y, z, w]

    def defaulted_param(
            self, x: int, y: int = 2, z: int = 3, w: int = 4) -> List[int]:
        """
        1 named param too many

        No pylint error
        """
        return [x, y, z, w]


class TooFew(Base):
    """1 param missing"""
    # overrides(Base.four_params)
    def four_params(self, x: int, z: int) -> List[int]:
        """
        1 param missing

        arguments-differ
        """
        return [x, z]

    def named_params(self, x: int, *, z: int) -> List[int]:
        """
        1 param missing

        arguments-differ
        """
        return [x, z]

    def defaulted_param(self, x: int, y: int = 2) -> List[int]:
        """
        1 param missing

        arguments-differ
        """
        return [x, y]


class Renamed(Base):
    """ 1 param renamed """
    # overrides(Base.four_params)
    def four_params(self, x: int, p: int, z: int) -> List[int]:
        """
        1 param renamed

        arguments-renamed
        """
        return [x, p, z]

    def named_params(self, x: int, *, p: int, z: int) -> List[int]:
        """
        1 param renamed

        arguments-differ
        """
        return [x, p, z]

    def defaulted_param(self, x: int, y: int = 2, p: int = 3) -> List[int]:
        """
        I have one defaulted param renamed

        arguments-renamed
        """
        return [x, y, p]


class ChangeNamed(Base):
    """ Changing which params have to be named """
    def four_params(self, x: int, y: int, *, z: int) -> List[int]:
        """
        More named

        arguments-differ
        """
        return [x, y, z]

    def named_params(self, x: int, y: int, *, z: int) -> List[int]:
        """
        Less named

        arguments-differ
        """
        return [x, y, z]

    def defaulted_param(self, x: int, y: int = 2, *, z: int = 3) -> List[int]:
        """
        default now named

        arguments-differ
        """
        return [x, y, z]

class ChangeOrder(Base):
    """ Changing order of params"""
    def four_params(self, x: int, z: int, y: int) -> List[int]:
        """I have four params including self"""
        return [x, y, z]

    def named_params(self, x: int, *, z: int, y: int) -> List[int]:
        """I have two unnamed (including self) and two named params"""
        return [x, y, z]

    def defaulted_param(self, x: int, z: int = 3, y: int = 2) -> List[int]:
        """ I have one defaulted param"""
        return [x, y, z]



# while if all works does not mean we like it
too_many = TooMany()
print(too_many.four_params(1, 2, 3, 4))
print(too_many.named_params(1, y=2, z=3, w=4))

too_many = ExtraDefaulted()
print(too_many.four_params(1, 2, 3, 4))
print(too_many.named_params(1, y=2, z=3, w=4))
print(too_many.defaulted_param(1, 2, 3, 4))

too_few = TooFew()
print(too_few.four_params(1, 2))
print(too_few.named_params(1, z=2))
print(too_few.defaulted_param(1, 2))

renamed = Renamed()
print(renamed.four_params(1, 2, 3))
print(renamed.named_params(1, p=2, z=3))
print(renamed.defaulted_param(1, 2, p=3))

change_named = ChangeNamed()
print(change_named.four_params(1, 2, z=3))
print(change_named.named_params(1, y=2, z=3))
print(change_named.defaulted_param(1, 2, z=3))

change_order = ChangeOrder()
print(change_order.four_params(1, 2, 3))
print(change_order.named_params(1, y=2, z=3))
print(change_order.defaulted_param(1, 2, 3))
