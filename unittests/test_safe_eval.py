import math
import pytest
from spinn_utilities.safe_eval import SafeEval


def Abc(x):
    return x+1


class Support(object):
    def __init__(self):
        self._c = 0

    def Def(self, x):
        return x*2

    def Ghi(self, x):
        return x*0.5

    def Jkl(self, x):
        self._c += 1
        return x + self._c**2


def test_simple_eval():
    evaluator = SafeEval()
    assert evaluator.eval("1+2*3") == 7
    assert evaluator.eval("x+y*z", x=1, y=2, z=3) == 7


def test_environment_eval():
    evaluator = SafeEval(Abc)
    assert evaluator.eval("Abc(1)") == 2
    with pytest.raises(NameError):
        evaluator.eval("Def(1)")
    with pytest.raises(TypeError):
        evaluator.eval("Abc(1,2)")


def test_multi_environment():
    s = Support()
    evaluator = SafeEval(Abc, s.Def)
    assert evaluator.eval("x+y*z", x=1, y=2, z=3) == 7
    assert evaluator.eval("Def(Abc(x))", x=3) == 8
    with pytest.raises(NameError):
        assert evaluator.eval("Ghi(Def(Abc(y)))", y=3) == 1
    assert evaluator.eval("Ghi(Def(Abc(y)))", y=3, Ghi=s.Ghi) == 4.0
    assert evaluator.eval("Ghi(Def(Abc(y)))", y=3, Ghi=s.Def) == 16
    # Not sure if the next test should pass; Python, huh...
    assert evaluator.eval("Ghi.__name__", y=3, Ghi=s.Def) == "Def"


def test_state_sensitive():
    s = Support()
    evaluator = SafeEval(s.Jkl)
    assert evaluator.eval("Jkl(Jkl(Jkl(x)))", x=2.5) == 16.5


def test_packages():
    evaluator = SafeEval(math)
    assert evaluator.eval("math.floor(d)", d=2.5) == 2.0


def test_defined_names():
    evaluator = SafeEval(math, x=123.25)
    assert evaluator.eval("math.floor(x+d)", d=0.875) == 124.0
