# pylint: disable=unused-variable, arguments-differ, signature-differs
import pytest
from spinn_utilities.overrides import overrides

WRONG_ARGS = "Method has {} arguments but super class method has 4 arguments"
BAD_DEFS = "Default arguments don't match super class method"


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
    class Sub(Base):
        @overrides(Base.foo)
        def foo(self, x, y, z):
            return super(Sub, self).foo(z, y, x)
    assert Sub().foo(1, 2, 3) == [3, 2, 1]


def test_doc_no_sub_extend():
    class Sub(Base):
        @overrides(Base.foo, extend_doc=True)
        def foo(self, x, y, z):
            return [z, y, x]
    assert Sub.foo.__doc__ == "this is the doc"


def test_doc_no_sub_no_extend():
    class Sub(Base):
        @overrides(Base.foo, extend_doc=False)
        def foo(self, x, y, z):
            return [z, y, x]
    assert Sub.foo.__doc__ == "this is the doc"


def test_doc_sub_no_extend():
    class Sub(Base):
        @overrides(Base.foo, extend_doc=False)
        def foo(self, x, y, z):
            """(abc)"""
            return [z, y, x]
    assert Sub.foo.__doc__ == "(abc)"


def test_doc_sub_extend():
    class Sub(Base):
        @overrides(Base.foo, extend_doc=True)
        def foo(self, x, y, z):
            """(abc)"""
            return [z, y, x]
    assert Sub.foo.__doc__ == "this is the doc(abc)"


def test_removes_param():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.foo)
            def foo(self, x, y):
                return [y, x]
    assert str(e.value) == WRONG_ARGS.format(3)


def test_adds_param():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.foo)
            def foo(self, x, y, z, w):
                return [w, z, y, x]
    assert str(e.value) == WRONG_ARGS.format(5)


def test_adds_expected_param():
    class Sub(Base):
        @overrides(Base.foo, additional_arguments=["w"])
        def foo(self, x, y, z, w):
            return [w, z, y, x]
    assert Sub().foo(1, 2, 3, 4) == [4, 3, 2, 1]


def test_renames_param():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.foo)
            def foo(self, x, y, w):
                return [w, y, x]
    assert str(e.value) == "Missing argument z"


def test_renames_param_expected():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.foo, additional_arguments=["w"])
            def foo(self, x, y, w):
                return [w, y, x]
    assert str(e.value) == WRONG_ARGS.format(4)
    # TODO: Fix the AWFUL error message in this case!


def test_changes_params_defaults():
    class Sub(Base):
        @overrides(Base.foodef)
        def foodef(self, x, y, z=False):
            return [z, y, x]
    assert Sub().foodef(1, 2) == [False, 2, 1]


def test_undefaults_super_param():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.foodef)
            def foodef(self, x, y, z):
                return [z, y, x]
    assert str(e.value) == BAD_DEFS


def test_defaults_super_param():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.foodef)
            def foodef(self, x, y=1, z=2):
                return [z, y, x]
    assert str(e.value) == BAD_DEFS
    # TODO: Should this case fail at all?


def test_defaults_super_param_expected():
    class Sub(Base):
        @overrides(Base.foodef, extend_defaults=True)
        def foodef(self, x, y=1, z=2):
            return [z, y, x]
    assert Sub().foodef(7) == [2, 1, 7]


def test_defaults_extra_param():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.foodef, additional_arguments=['pdq'])
            def foodef(self, x, y, z=1, pdq=2):
                return [z, y, x, pdq]
    assert str(e.value) == BAD_DEFS


def test_defaults_super_param_no_super_defaults():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.foo)
            def foo(self, x, y, z=7):
                return [z, y, x]
    assert str(e.value) == BAD_DEFS
    # TODO: Should this case fail at all?


def test_crazy_extends():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.foo)
            def bar(self, x, y, z):
                return [z, y, x]
    assert str(e.value) == \
        "Super class method name foo does not match bar. Ensure override is "\
        "the last decorator before the method declaration"


def test_overrides_property():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.boo)
            @property
            def boo(self):
                return 1513
    assert str(e.value) == \
        "Please ensure that the override decorator is the last decorator "\
        "before the method declaration"


def test_property_overrides():
    class Sub(Base):
        @property
        @overrides(Base.boo)
        def boo(self):
            return 1513
    assert Sub().boo == 1513
