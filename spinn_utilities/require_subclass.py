# Copyright (c) 2021 The University of Manchester
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


class _RequiresSubclassTypeError(TypeError):
    """
    A special exception to handle just the case where the decorator is applied
    so that we can easily figure out when to pass on the extra meta-arguments.

    Do not use outside this file. Outsiders should just see ``TypeError``.
    """


def require_subclass(required_class):
    """
    Decorator that arranges for subclasses of the decorated class to
    require that they are also subclasses of the given class.

    Usage example::

        @require_subclass(AbstractVertex)
        class AbstractVirtual(object):
            ...

    :param type required_class:
        The class that the subclass of the decorated class must be an instance
        of (if that subclass is concrete).
    """

    # Beware! This is all deep shenanigans!
    #
    # The __init_subclass__ stuff is from
    #     https://stackoverflow.com/a/45400374/301832
    # The setattr() call is from:
    #     https://stackoverflow.com/a/533583/301832
    # The classmethod() call is from:
    #     https://stackoverflow.com/a/17930262/301832
    # The use of __class__ to enable super() to work is from:
    #     https://stackoverflow.com/a/43779009/301832
    # The need to do this as a functional decorator is my own discovery;
    # without it, some very weird interactions with metaclasses happen and I
    # really don't want to debug that stuff.

    def decorate(target_class):
        # pylint: disable=unused-variable
        __class__ = target_class  # @ReservedAssignment # noqa: F841

        def __init_subclass__(cls, allow_derivation=False, **kwargs):
            if not issubclass(cls, required_class) and not allow_derivation:
                raise _RequiresSubclassTypeError(
                    f"{cls.__name__} must be a subclass "
                    f"of {required_class.__name__} and the derivation was not "
                    "explicitly allowed with allow_derivation=True")
            try:
                super().__init_subclass__(**kwargs)
            except _RequiresSubclassTypeError:
                super().__init_subclass__(
                    allow_derivation=allow_derivation, **kwargs)

        setattr(target_class, '__init_subclass__',
                classmethod(__init_subclass__))
        return target_class
    return decorate
