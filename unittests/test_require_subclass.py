# Copyright (c) 2018-2019 The University of Manchester
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

# pylint: disable=unused-variable
import pytest
from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from spinn_utilities.require_subclass import require_subclass


class Base(object):
    def __init__(self):
        self.bar = 123


@require_subclass(Base)
class Ifc(object, metaclass=AbstractBase):
    @abstractmethod
    def foo(self):
        pass


@require_subclass(Base)
class Ifc2(object, metaclass=AbstractBase):
    @abstractmethod
    def bacon(self):
        pass


class NotFromBase(object):
    def __init__(self):
        self.bar = 234


class FromBase(Base):
    def __init__(self):
        super().__init__()
        self.grill = 345


class DerivedIfc(Ifc, allow_derivation=True):
    pass


class DoubleDerivedIfc(Ifc, Ifc2, allow_derivation=True):
    pass


def test_direct():
    class Foo1(FromBase, Ifc):
        def foo(self):
            pass
    assert Foo1().bar == 123


def test_indirect():
    class Foo2(FromBase, DerivedIfc):
        def foo(self):
            pass
    assert Foo2().bar == 123


def test_non_base_direct():
    with pytest.raises(TypeError, match="Foo3 must be a subclass of Base"):
        class Foo3(NotFromBase, Ifc):
            def foo(self):
                pass
        assert Foo3().bar == 234


def test_non_base_indirect():
    with pytest.raises(TypeError, match="Foo4 must be a subclass of Base"):
        class Foo4(NotFromBase, DerivedIfc):
            def foo(self):
                pass
        assert Foo4().bar == 234


def test_non_base_double_indirect():
    with pytest.raises(TypeError, match="Foo6 must be a subclass of Base"):
        class Foo5(DerivedIfc, allow_derivation=True):
            def foo(self):
                pass

        class Foo6(NotFromBase, Foo5):
            def foo(self):
                pass
        assert Foo6().bar == 234


def test_double_indirect():
    class Foo7(FromBase, DoubleDerivedIfc):
        def foo(self):
            pass

        def bacon(self):
            pass
    assert Foo7().bar == 123


def test_non_base_double_indirect_other():
    with pytest.raises(TypeError, match="Foo8 must be a subclass of Base"):
        class Foo8(NotFromBase, DoubleDerivedIfc):
            def foo(self):
                pass

            def bacon(self):
                pass
        assert Foo8().bar == 123
