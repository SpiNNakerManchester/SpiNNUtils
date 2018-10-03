from spinn_utilities.classproperty import classproperty


class ClassWithClassProperty(object):

    _my_property = "Test"
    getter_called = False

    @classproperty
    def my_property(cls):
        cls.getter_called = True
        return cls._my_property

    @classmethod
    def set_my_property(cls, my_property):
        cls._my_property = my_property


def test_class_property():

    assert not ClassWithClassProperty.getter_called
    assert ClassWithClassProperty.my_property == \
        ClassWithClassProperty._my_property
    assert ClassWithClassProperty.getter_called

    instance_1 = ClassWithClassProperty()
    instance_2 = ClassWithClassProperty()
    ClassWithClassProperty.set_my_property("NewValue")
    assert instance_1.my_property == instance_2.my_property
    assert ClassWithClassProperty.my_property == instance_1.my_property
