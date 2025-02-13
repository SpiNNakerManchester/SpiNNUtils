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

from spinn_utilities.classproperty import classproperty


class ClassWithClassProperty(object):

    _my_property = "Test"
    getter_called = False

    @classproperty
    def my_property(cls) -> str:
        cls.getter_called = True
        return cls._my_property

    @classmethod
    def set_my_property(cls, my_property: str) -> None:
        cls._my_property = my_property


def test_class_property() -> None:

    assert not ClassWithClassProperty.getter_called
    assert ClassWithClassProperty.my_property == \
        ClassWithClassProperty._my_property
    assert ClassWithClassProperty.getter_called

    instance_1 = ClassWithClassProperty()
    instance_2 = ClassWithClassProperty()
    ClassWithClassProperty.set_my_property("NewValue")
    assert instance_1.my_property == instance_2.my_property
    assert ClassWithClassProperty.my_property == instance_1.my_property
