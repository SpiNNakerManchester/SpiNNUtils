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
from typing import Any, List
from spinn_utilities.abstract_base import abstractmethod
from spinn_utilities.overrides import overrides

WRONG_ARGS = "Method has {} arguments but super class method has 4 arguments"
BAD_DEFS = "Default arguments don't match super class method"

overrides.check_types()


class Base(object):
    def foo(self, x: int, y: int, z: int) -> List[int]:
        """this is the doc"""
        return [x, y, z]

    def foodef(self, x: Any, y: int, z: Any = True) -> List[Any]:
        """this is the doc"""
        return [x, y, z]

    @property
    def boo(self) -> int:
        return 123

    def with_param_no_return(self, x: int) -> None:
        pass

    def with_param_no_return2(self, x: int):
        pass

    def no_param_no_return(self):
        pass

    # This is bad as it does not define a return
    def bad(self, x: int, y: int, z: int):
        """this is the doc"""
        return [x, y, z]


def test_basic_use():
    class Sub(Base):
        @overrides(Base.foo)
        def foo(self, x: int, y: int, z: int) -> List[int]:
            return super().foo(z, y, x)
    assert Sub().foo(1, 2, 3) == [3, 2, 1]


def test_doc_no_sub_extend():
    class Sub(Base):
        @overrides(Base.foo, extend_doc=True)
        def foo(self, x: int, y: int, z: int) -> List[int]:
            return [z, y, x]
    assert Sub.foo.__doc__ == "this is the doc"


def test_doc_no_sub_no_extend():
    class Sub(Base):
        @overrides(Base.foo, extend_doc=False)
        def foo(self, x: int, y: int, z: int) -> List[int]:
            return [z, y, x]
    assert Sub.foo.__doc__ == "this is the doc"


def test_doc_sub_no_extend():
    class Sub(Base):
        @overrides(Base.foo, extend_doc=False)
        def foo(self, x: int, y: int, z: int) -> List[int]:
            """(abc)"""
            return [z, y, x]
    assert Sub.foo.__doc__ == "(abc)"


def test_doc_sub_extend():
    class Sub(Base):
        @overrides(Base.foo, extend_doc=True)
        def foo(self, x: int, y: int, z: int) -> List[int]:
            """(abc)"""
            return [z, y, x]
    assert Sub.foo.__doc__ == "this is the doc(abc)"


def test_removes_param():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.foo)
            def foo(self, x: int, y: int) -> List[int]:
                return [y, x]
    assert str(e.value) == WRONG_ARGS.format(3)


def test_adds_param():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.foo)
            def foo(self, x: int, y: int, z: int, w: int) -> List[int]:
                return [w, z, y, x]
    assert str(e.value) == WRONG_ARGS.format(5)


def test_adds_expected_param():
    class Sub(Base):
        @overrides(Base.foo, additional_arguments=["w"])
        def foo(self, x: int, y: int, z: int, w: int) -> List[int]:
            return [w, z, y, x]
    assert Sub().foo(1, 2, 3, 4) == [4, 3, 2, 1]


def test_renames_param():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.foo)
            def foo(self, x: int, y: int, w: int) -> List[int]:
                return [w, y, x]
    assert str(e.value) == "Missing argument z"


def test_renames_param_expected():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.foo, additional_arguments=["w"])
            def foo(self, x: int, y: int, w: int) -> List[int]:
                return [w, y, x]
    assert str(e.value) == WRONG_ARGS.format(4)
    # TODO: Fix the AWFUL error message in this case!


def test_changes_params_defaults():
    class Sub(Base):
        @overrides(Base.foodef)
        def foodef(self, x: Any, y: Any, z: Any = False) -> List[Any]:
            return [z, y, x]
    assert Sub().foodef(1, 2) == [False, 2, 1]


def test_undefaults_super_param():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.foodef)
            def foodef(self, x: Any, y: Any, z: Any) -> List[Any]:
                return (z, y, x)
    assert str(e.value) == BAD_DEFS


def test_defaults_super_param():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.foodef)
            def foodef(self, x: Any, y: Any = 1, z: Any = 2) -> List[Any]:
                return [z, y, x]
    assert str(e.value) == BAD_DEFS
    # TODO: Should this case fail at all?


def test_defaults_super_param_expected():
    class Sub(Base):
        @overrides(Base.foodef, extend_defaults=True)
        def foodef(self, x: Any, y: Any = 1, z: Any = 2) -> List[Any]:
            return [z, y, x]
    assert Sub().foodef(7) == [2, 1, 7]


def test_defaults_extra_param():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.foodef, additional_arguments=['pdq'])
            def foodef(self, x: Any, y: Any, z: Any = 1, pdq: Any = 2
                       ) -> List[Any]:
                return [z, y, x, pdq]
    assert str(e.value) == BAD_DEFS


def test_defaults_super_param_no_super_defaults():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.foo)
            def foo(self, x: int, y: int, z: int = 7) -> List[int]:
                return [z, y, x]
    assert str(e.value) == BAD_DEFS
    # TODO: Should this case fail at all?


def test_crazy_extends():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.foo)
            def bar(self, x: int, y: int, z: int):
                return [z, y, x]
    assert str(e.value) == \
        "super class method name foo does not match bar. Ensure overrides is "\
        "the last decorator before the method declaration"


def test_overrides_property() -> None:
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.boo)  # type: ignore[misc]
            @property
            def boo(self) -> int:
                return 1513
    assert str(e.value) == \
        "Please ensure that the overrides decorator is the last decorator "\
        "before the method declaration"


def test_property_overrides() -> None:
    class Sub(Base):
        @property
        @overrides(Base.boo)
        def boo(self) -> int:
            return 1513
    assert Sub().boo == 1513


def test_sister_overides() -> None:
    class ParentOne(object):
        @abstractmethod
        def foo(self) -> int:
            raise NotImplementedError

    class ParentTwo(object):
        @overrides(ParentOne.foo)
        @abstractmethod
        def foo(self) -> int:
            raise NotImplementedError

        def bar(self):
            return self.foo()

    class Child(ParentTwo, ParentOne):
        @overrides(ParentTwo.foo)
        @overrides(ParentOne.foo)
        def foo(self) -> int:
            return 1

    a = Child()
    assert 1 == a.bar()


def test_sister_overides_bad() -> None:
    class ParentOne(object):
        @abstractmethod
        def foo(self) -> int:
            raise NotImplementedError

    class ParentTwo(object):

        try:
            @overrides(ParentOne.foo)
            @abstractmethod
            def foo(self, check) -> int:
                raise NotImplementedError

            raise ValueError("Should not get here")
        except AttributeError:
            pass


def test_sister_different1() -> None:
    class ParentOne(object):
        @abstractmethod
        def foo(self) -> int:
            raise NotImplementedError

    class ParentTwo(object):
        @abstractmethod
        def foo(self, check) -> int:
            raise NotImplementedError

        def bar(self):
            return self.foo()

    try:
        class Child(ParentTwo, ParentOne):
            @overrides(ParentTwo.foo)
            @overrides(ParentOne.foo)
            def foo(self) -> int:
                return 1
    except AttributeError:
        pass


def test_sister_different2() -> None:
    class ParentOne(object):
        @abstractmethod
        def foo(self) -> int:
            raise NotImplementedError

    class ParentTwo(object):
        @abstractmethod
        def foo(self, check) -> int:
            raise NotImplementedError

        def bar(self):
            return self.foo()

    try:
        class Child(ParentTwo, ParentOne):
            @overrides(ParentOne.foo)
            @overrides(ParentTwo.foo)
            def foo(self) -> int:
                return 1
    except AttributeError:
        pass


def test_add_return():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.bad)
            def bad(self, x: int, y: int, z: int) -> List[int]:
                return super().foo(z, y, x)
    assert str(e.value) == "Super Method bad has no return type, " \
                           "while this does"


def test_dont_add_return():
    # This demonstrates that if both have no return we can not check it.
    # It would be better if there was an error!
    class Sub(Base):
        @overrides(Base.bad)
        def bad(self, x: int, y: int, z: int):
            return super().foo(z, y, x)
    assert Sub().bad(1, 2, 3) == [3, 2, 1]


def test_missing_return_type():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @property
            @overrides(Base.boo)
            def boo(self):
                return 2
    assert str(e.value) == "Method boo has no arguments " \
                           "so should declare a return type"


def test_with_missing_return():
    class Sub(Base):
        @overrides(Base.with_param_no_return)
        def with_param_no_return(self, x: int):
            pass


def test_with_missing_return_both():
    class Sub(Base):
        @overrides(Base.with_param_no_return2)
        def with_param_no_return2(self, x: int):
            pass


def test_with_missing_return_super():
    class Sub(Base):
        @overrides(Base.with_param_no_return2)
        def with_param_no_return2(self, x: int) -> None:
            pass


def test_no_param_missing_return():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.no_param_no_return)
            def no_param_no_return(self):
                pass
    assert str(e.value) == "Super Method no_param_no_return has " \
                           "no arguments so should declare a return type"
