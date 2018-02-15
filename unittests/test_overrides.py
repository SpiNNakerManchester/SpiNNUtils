from spinn_utilities.overrides import overrides
import pytest


class Base(object):
    def foo(self, x, y, z):
        """this is the doc"""
        return [x, y, z]

    @property
    def boo(self):
        return 123


def test_doc():
    class Sub(Base):
        @overrides(Base.foo, extend_doc=True)
        def foo(self, x, y, z):
            return [z, y, x]
    assert Sub.foo.__doc__ == "this is the doc"

    class Sub2(Base):
        @overrides(Base.foo, extend_doc=False)
        def foo(self, x, y, z):
            return [z, y, x]
    assert Sub2.foo.__doc__ == "this is the doc"

    class Sub3(Base):
        @overrides(Base.foo, extend_doc=False)
        def foo(self, x, y, z):
            """(abc)"""
            return [z, y, x]
    assert Sub3.foo.__doc__ == "(abc)"

    class Sub4(Base):
        @overrides(Base.foo, extend_doc=True)
        def foo(self, x, y, z):
            """(abc)"""
            return [z, y, x]
    assert Sub4.foo.__doc__ == "this is the doc(abc)"


def test_changes_params():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.foo)
            def foo(self, x, y):
                return [y, x]
    assert e.value.message == \
        "Method has 3 arguments but super class method has 4 arguments"

    with pytest.raises(AttributeError) as e:
        class Sub2(Base):
            @overrides(Base.foo)
            def foo(self, x, y, z, w):
                return [w, z, y, x]
    assert e.value.message == \
        "Method has 5 arguments but super class method has 4 arguments"

    class Sub3(Base):
        @overrides(Base.foo, additional_arguments=["w"])
        def foo(self, x, y, z, w):
            return [w, z, y, x]

    with pytest.raises(AttributeError) as e:
        class Sub4(Base):
            @overrides(Base.foo, additional_arguments=["w"])
            def foo(self, x, y, w):
                return [w, y, x]
    assert e.value.message == \
        "Method has 4 arguments but super class method has 4 arguments"
    # TODO: Fix the AWFUL error message in this case!


def test_crazy_extends():
    with pytest.raises(AttributeError) as e:
        class Sub(Base):
            @overrides(Base.foo)
            def bar(self, x, y, z):
                return [z, y, x]
    assert e.value.message == \
        "Super class method name foo does not match bar. Ensure override is "\
        "the last decorator before the method declaration"

    with pytest.raises(AttributeError) as e:
        class Sub2(Base):
            @overrides(Base.boo)
            @property
            def boo(self):
                return 1513
    assert e.value.message == \
        "Please ensure that the override decorator is the last decorator "\
        "before the method declaration"

    class Sub3(Base):
        @property
        @overrides(Base.boo)
        def boo(self):
            return 1513
    assert Sub3().boo == 1513
