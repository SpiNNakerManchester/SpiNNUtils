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


class SafeEval(object):
    """
    This provides expression evaluation capabilities while allowing the
    set of symbols exposed to the expression to be strictly controlled.

    Sample of use::

        >>> import math
        >>> def evil_func(x):
        ...    print("HAHA!")
        ...    return x/0.0
        ...
        >>> eval_safely = SafeEval(math)
        >>> eval_safely.eval("math.sqrt(x)", x=1.23)
        1.1090536506409416
        >>> eval_safely.eval("evil_func(1.23)")
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File ".../safe_eval.py", line 62, in eval
            return eval(expression, self._environment, kwargs)
          File "<string>", line 1, in <module>
        NameError: name 'evil_func' is not defined

    .. warning::
        This is not guaranteed to be safe under all circumstances. It is not
        designed to be a fully secured interface; it just *discourages* abuse.
    """
    __slots__ = ["_environment"]

    def __init__(self, *args, **kwargs):
        """
        :param args:
            The symbols to use to populate the global reference table.

            .. note::
                All of these symbols must support the `__name__` property, but
                that includes any function, method of an object, or module. If
                you want to make an object available by anything other than its
                inherent name, define it in the
                :py:meth:`eval` call.
        :param kwargs:
            Define the symbols with explicit names. Needed because some
            symbols (e.g., constants in numpy) do not have names that we can
            otherwise look up easily.
        """
        env = {}
        for item in args:
            env[item.__name__] = item
        env.update(kwargs)
        self._environment = env

    def eval(self, expression, **kwargs):
        """
        Evaluate an expression and return the result.

        :param expression: The expression to evaluate
        :type expression: str
        :param kwargs:
            The extra symbol bindings to use for this evaluation.
            This is useful for passing in particular parameters to an
            individual evaluation run.
        :return: The expression result, the type of which will depend on the
            expression itself and the operations exposed to it.
        """
        # pylint: disable=eval-used
        return eval(expression, self._environment, kwargs)
