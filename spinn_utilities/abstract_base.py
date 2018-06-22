# Trimmed down version of abc.py

# If using #@add_metaclass require from six import add_metaclass


def abstractmethod(funcobj):
    """ A decorator indicating abstract methods.

    Requires that the metaclass is :py:class:`AbstractBase` or derived from\
    it. A class that has a metaclass derived from :py:class:`AbstractBase` \
    cannot be instantiated unless all of its abstract methods are overridden.\
    The abstract methods can be called using any of the normal\
    'super' call mechanisms.

    Usage::

        @add_metaclass(AbstractBase)
        class C:
            @abstractmethod
            def my_abstract_method(self, ...):
            ...
    """
    funcobj.__isabstractmethod__ = True
    return funcobj


class abstractproperty(property):
    """ A decorator indicating abstract properties.

    Requires that the metaclass is :py:class:`AbstractBase` or derived from\
    it. A class that has a metaclass derived from :py:class:`AbstractBase` \
    cannot be instantiated unless all of its abstract properties are\
    overridden. The abstract properties can be called using any of the normal\
    'super' call mechanisms.

    Usage::

        @add_metaclass(AbstractBase)
        class C:
            @abstractproperty
            def my_abstract_property(self):
                ...

    This defines a read-only property; you can also define a read-write\
    abstract property using the 'long' form of property declaration::

        @add_metaclass(AbstractBase)
        class C:
            def getx(self): ...
            def setx(self, value): ...
            x = abstractproperty(getx, setx)
    """
    __isabstractmethod__ = True


class AbstractBase(type):
    """ Metaclass for defining Abstract Base Classes (AbstractBases).

    Use this metaclass to create an AbstractBase. An AbstractBase can be\
    subclassed directly, and then acts as a mix-in class.

    This is a trimmed down version of ABC.\
    Unlike ABC you can not register unrelated concrete classes.
    """

    def __new__(cls, name, bases, namespace):
        # Actually make the class
        abs_cls = super(AbstractBase, cls).__new__(cls, name, bases, namespace)

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
