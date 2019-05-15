# Copyright (c) 2017-2018 The University of Manchester
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

class SafeEval(object):
    """ This provides expression evaluation capabilities while allowing the\
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
        This is not guaranteed to be safe under all circumstances. It\
        is not designed to be a fully secured interface; it just\
        *discourages* abuse.
    """
    __slots__ = ["_environment"]

    def __init__(self, *args, **kwargs):
        """
        :param args:\
            The symbols to use to populate the global reference table. \
            Note that all of these symbols must support the `__name__`\
            property, but that includes any function, method of an object, or\
            module. If you want to make an object available by anything other\
            than its inherent name, define it in the\
            :py:meth:`eval` call.
        :param kwargs:\
            Define the symbols with explicit names. Needed because some\
            symbols (e.g., constants in numpy) do not have names that we can\
            otherwise look up easily.
        """
        env = {}
        for item in args:
            env[item.__name__] = item
        env.update(kwargs)
        self._environment = env

    def eval(self, expression, **kwargs):
        """ Evaluate an expression and return the result.

        :param expression: The expression to evaluate
        :type expression: str
        :param kwargs:\
            The extra symbol bindings to use for this evaluation. \
            This is useful for passing in particular parameters to an\
            individual evaluation run.
        :return: The expression result, the type of which will depend on the\
            expression itself and the operations exposed to it.
        """
        # pylint: disable=eval-used
        return eval(expression, self._environment, kwargs)
