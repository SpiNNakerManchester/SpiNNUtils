# Copyright (c) 2018 The University of Manchester
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


class NotFromBase(object):
    def __init__(self):
        self.bar = 234


class FromBase(Base):
    def __init__(self):
        super().__init__()
        self.grill = 345


class DerivedIfc(Ifc, allow_derivation=True):
    pass


@require_subclass(Base)
class Ifc2(object, metaclass=AbstractBase):
    @abstractmethod
    def bar(self):
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


def test_double():
    class Foo7(FromBase, Ifc, Ifc2):
        pass


def test_double_indirect():
    class Ifc3(Ifc, Ifc2, allow_derivation=True):
        pass

    class Foo7(FromBase, Ifc3):
        def foo(self):
            return 123

        def bar(self):
            return 234

    assert Foo7() is not None
