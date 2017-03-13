class SafeEval(object):
    __slots__ = ["_environment"]

    def __init__(self, *args):
        env = {}
        for item in args:
            env[item.__name__] = item
        self._environment = env

    def eval(self, expression, **kwargs):
        return eval(expression, self._environment, kwargs)
