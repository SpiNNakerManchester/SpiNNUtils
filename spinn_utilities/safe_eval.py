class SafeEval(object):
    """ This provides expression evaluation capabilities while allowing the\
        set of symbols exposed to the expression to be strictly controlled.

    Sample of use:

    >>> import math
    >>> def evil_func(x):
           print "HAHA!"
           return x/0.0

    >>> eval_safely = SafeEval(math)
    >>> eval_safely.eval("math.sqrt(x)", x=1.23)
    1.1090536506409416
    >>> eval_safely.eval("evil_func(1.23)")
    Traceback (most recent call last):
      ...
    NameError: name 'evil_func' is not defined
    """
    __slots__ = ["_environment"]

    def __init__(self, *args, **kwargs):
        """
        :param args:\
            The symbols to use to populate the global reference table.
            Note that all of these symbols must support the __name__ property,\
            but that includes any function, method of an object, or module. If\
            you want to make an object available by anything other than its\
            inherent name, define it in the eval() call.
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
            The extra symbol bindings to use for this evaluation.
            This is useful for passing in particular parameters to an\
            individual evaluation run.
        :return: The expression result
        """
        return eval(expression, self._environment, kwargs)
