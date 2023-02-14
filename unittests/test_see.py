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

from spinn_utilities.see import see
import pytest

WRONG_ARGS = "Method has {} arguments but documentation method has 4 arguments"
BAD_DEFS = "Default arguments don't match documentation method"


class Base(object):
    def foo(self, x, y, z):
        """this is the doc"""
        return [x, y, z]

    def foodef(self, x, y, z=True):
        """this is the doc"""
        return [x, y, z]

    @property
    def boo(self):
        return 123


def test_basic_use():
    class Sub(object):
        @see(Base.foo)
        def foo(self, x, y, z):
            return None


def test_doc_no_sub_extend():
    class Sub(object):
        @see(Base.foo, extend_doc=True)
        def foo(self, x, y, z):
            return [z, y, x]
    assert Sub.foo.__doc__ == "this is the doc"


def test_doc_no_sub_no_extend():
    class Sub(object):
        @see(Base.foo, extend_doc=False)
        def foo(self, x, y, z):
            return [z, y, x]
    assert Sub.foo.__doc__ == "this is the doc"


def test_doc_sub_no_extend():
    class Sub(object):
        @see(Base.foo, extend_doc=False)
        def foo(self, x, y, z):
            """(abc)"""
            return [z, y, x]
    assert Sub.foo.__doc__ == "(abc)"


def test_doc_sub_extend():
    class Sub(object):
        @see(Base.foo, extend_doc=True)
        def foo(self, x, y, z):
            """(abc)"""
            return [z, y, x]
    assert Sub.foo.__doc__ == "this is the doc(abc)"


def test_removes_param():
    with pytest.raises(AttributeError) as e:
        class Sub(object):
            @see(Base.foo)
            def foo(self, x, y):
                return [y, x]
    assert str(e.value) == WRONG_ARGS.format(3)


def test_adds_param():
    with pytest.raises(AttributeError) as e:
        class Sub(object):
            @see(Base.foo)
            def foo(self, x, y, z, w):
                return [w, z, y, x]
    assert str(e.value) == WRONG_ARGS.format(5)


def test_adds_expected_param():
    class Sub(object):
        @see(Base.foo, additional_arguments=["w"])
        def foo(self, x, y, z, w):
            return [w, z, y, x]
    assert Sub().foo(1, 2, 3, 4) == [4, 3, 2, 1]


def test_renames_param():
    with pytest.raises(AttributeError) as e:
        class Sub(object):
            @see(Base.foo)
            def foo(self, x, y, w):
                return [w, y, x]
    assert str(e.value) == "Missing argument z"


def test_renames_param_expected():
    with pytest.raises(AttributeError) as e:
        class Sub(object):
            @see(Base.foo, additional_arguments=["w"])
            def foo(self, x, y, w):
                return [w, y, x]
    assert str(e.value) == WRONG_ARGS.format(4)
    # TODO: Fix the AWFUL error message in this case!


def test_changes_params_defaults():
    class Sub(object):
        @see(Base.foodef)
        def foodef(self, x, y, z=False):
            return [z, y, x]
    assert Sub().foodef(1, 2) == [False, 2, 1]


def test_undefaults_super_param():
    with pytest.raises(AttributeError) as e:
        class Sub(object):
            @see(Base.foodef)
            def foodef(self, x, y, z):
                return [z, y, x]
    assert str(e.value) == BAD_DEFS


def test_defaults_super_param():
    with pytest.raises(AttributeError) as e:
        class Sub(object):
            @see(Base.foodef)
            def foodef(self, x, y=1, z=2):
                return [z, y, x]
    assert str(e.value) == BAD_DEFS
    # TODO: Should this case fail at all?


def test_defaults_super_param_expected():
    class Sub(object):
        @see(Base.foodef, extend_defaults=True)
        def foodef(self, x, y=1, z=2):
            return [z, y, x]
    assert Sub().foodef(7) == [2, 1, 7]


def test_defaults_extra_param():
    with pytest.raises(AttributeError) as e:
        class Sub(object):
            @see(Base.foodef, additional_arguments=['pdq'])
            def foodef(self, x, y, z=1, pdq=2):
                return [z, y, x, pdq]
    assert str(e.value) == BAD_DEFS


def test_defaults_super_param_no_super_defaults():
    with pytest.raises(AttributeError) as e:
        class Sub(object):
            @see(Base.foo)
            def foo(self, x, y, z=7):
                return [z, y, x]
    assert str(e.value) == BAD_DEFS
    # TODO: Should this case fail at all?


def test_doc_only_extends():
    class Sub(object):
        @see(Base.foo)
        def bar(self, x, y, z):
            return [z, y, x]


def test_overrides_property():
    with pytest.raises(AttributeError) as e:
        class Sub(object):
            @see(Base.boo)
            @property
            def boo(self):
                return 1513
    assert str(e.value) == \
        "Please ensure that the see decorator is the last decorator "\
        "before the method declaration"


def test_property_overrides():
    class Sub(object):
        @property
        @see(Base.boo)
        def boo(self):
            return 1513
    assert Sub().boo == 1513
