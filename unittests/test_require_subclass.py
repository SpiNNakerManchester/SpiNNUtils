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

import pytest
from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from spinn_utilities.require_subclass import require_subclass


class Base(object):
    @property
    def bar(self) -> int:
        return 123


@require_subclass(Base)
class Ifc(object, metaclass=AbstractBase):
    @abstractmethod
    def foo(self) -> None:
        pass


class NotFromBase(object):
    def __init__(self) -> None:
        self.bar = 234


class FromBase(Base):
    def __init__(self) -> None:
        super().__init__()
        self.grill = 345


class DerivedIfc(Ifc, allow_derivation=True):
    pass


@require_subclass(Base)
class Ifc2(object, metaclass=AbstractBase):
    @property
    @abstractmethod
    def bar(self) -> int:
        raise NotImplementedError()


def test_direct() -> None:
    class Foo1(FromBase, Ifc):
        def foo(self) -> None:
            pass
    assert Foo1().bar == 123


def test_indirect() -> None:
    class Foo2(FromBase, DerivedIfc):
        def foo(self) -> None:
            pass
    assert Foo2().bar == 123


def test_non_base_direct() -> None:
    with pytest.raises(TypeError, match="Foo3 must be a subclass of Base"):
        class Foo3(NotFromBase, Ifc):
            def foo(self) -> None:
                pass
        assert Foo3().bar == 234


def test_non_base_indirect() -> None:
    with pytest.raises(TypeError, match="Foo4 must be a subclass of Base"):
        class Foo4(NotFromBase, DerivedIfc):
            def foo(self) -> None:
                pass
        assert Foo4().bar == 234


def test_non_base_double_indirect() -> None:
    with pytest.raises(TypeError, match="Foo6 must be a subclass of Base"):
        class Foo5(DerivedIfc, allow_derivation=True):
            def foo(self) -> None:
                pass

        class Foo6(NotFromBase, Foo5):
            def foo(self) -> None:
                pass
        assert Foo6().bar == 234


def test_double() -> None:
    class Foo7(FromBase, Ifc, Ifc2):
        pass


def test_double_indirect() -> None:
    class Ifc3(Ifc, Ifc2, allow_derivation=True):
        pass

    class Foo7(FromBase, Ifc3):
        def foo(self) -> None:
            assert True

        @property
        def bar(self) -> int:
            return 234

    assert Foo7() is not None
