# Copyright (c) 2018 The University of Manchester
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
