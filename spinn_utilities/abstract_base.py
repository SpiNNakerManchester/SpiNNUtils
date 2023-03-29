# Copyright (c) 2017 The University of Manchester
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
"""
A trimmed down version of standard Python Abstract Base classes.
"""


def abstractmethod(funcobj):
    """
    A decorator indicating abstract methods.

    Requires that the metaclass is :py:class:`AbstractBase` or derived from
    it. A class that has a metaclass derived from :py:class:`AbstractBase`
    cannot be instantiated unless all of its abstract methods are overridden.
    The abstract methods can be called using any of the normal
    'super' call mechanisms.

    Usage::

        class C(object, metaclass=AbstractBase):
            @abstractmethod
            def my_abstract_method(self, ...):
                ...
    """
    funcobj.__isabstractmethod__ = True
    return funcobj


class abstractproperty(property):
    """
    A decorator indicating abstract properties.

    Requires that the metaclass is :py:class:`AbstractBase` or derived from
    it. A class that has a metaclass derived from :py:class:`AbstractBase`
    cannot be instantiated unless all of its abstract properties are
    overridden. The abstract properties can be called using any of the normal
    'super' call mechanisms.

    Usage::

        class C(object, metaclass=AbstractBase):
            @abstractproperty
            def my_abstract_property(self):
                ...

    This defines a read-only property; you can also define a read-write
    abstract property using the 'long' form of property declaration::

        class C(object, metaclass=AbstractBase):
            def getx(self): ...
            def setx(self, value): ...
            x = abstractproperty(getx, setx)

    .. note::
        When documenting abstract properties, remember to document them as if
        they are nouns, not verbs; they are things about the object that may
        be observed as many times as the user of the class desires.

    .. warning::
        Implementations should be idempotent; fetching the property twice in a
        row should get an equivalent value with no (meaningful) change to the
        state of the object (assuming no other non-property methods of the
        object are invoked between).

        This is an assumption that debuggers make. *Do not violate it!*
    """
    __isabstractmethod__ = True


class AbstractBase(type):
    """
    Metaclass for defining Abstract Base Classes (AbstractBases).

    Use this metaclass to create an AbstractBase. An AbstractBase can be
    subclassed directly, and then acts as a mix-in class.

    This is a trimmed down version of ABC.
    Unlike ABC you can not register unrelated concrete classes.

    Usage::

        class C(object, metaclass=AbstractBase):
            @abstractmethod
            def my_abstract_method(self, ...):
                ...
    """

    def __new__(cls, name, bases, namespace, **kwargs):
        # Actually make the class
        abs_cls = super().__new__(cls, name, bases, namespace, **kwargs)

        # Get set of abstract methods from namespace
        abstracts = set(nm for nm, val in namespace.items()
                        if getattr(val, "__isabstractmethod__", False))

        # Augment with abstract methods from superclasses
        for base in bases:
            for nm in getattr(base, "__abstractmethods__", set()):
                val = getattr(abs_cls, nm, None)
                if getattr(val, "__isabstractmethod__", False):
                    abstracts.add(nm)

        # Lock down the set
        abs_cls.__abstractmethods__ = frozenset(abstracts)
        return abs_cls
