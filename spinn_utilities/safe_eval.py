class SafeEval(object):
    __slots__ = ["_environment"]

    def __init__(self, *args):
        env = {}
        for item in args:
            env[item.__name__] = item
        self._environment = env

    def eval(self, expression, **kwargs):
        return eval(expression, self._environment, kwargs)


if __name__ == "__main__":
    def Abc(x):
        return x+1
    def Def(x):
        return x*2
    def Ghi(x):
        return x*0.5

    evaluator = SafeEval(Abc, Def)
    def test(string, **args):
        try:
            result = evaluator.eval(string, **args)
            print string, "=", result
        except NameError:
            print "failed to evaluate", string
    test("Def(Abc(x))", x=3)
    test("Ghi(Def(Abc(y)))", y=3)
