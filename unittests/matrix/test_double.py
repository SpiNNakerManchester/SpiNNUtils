from spinn_utilities.matrix.double_dict import DoubleDict
from spinn_utilities.matrix.demo_matrix import DemoMatrix


def test_insert():
    matrix = DemoMatrix()
    matrix.set_data("Foo", 1, "One")
    double = DoubleDict(xtype=str, ytype=int, matrix=matrix)
    assert double["Foo"][1] == "One"
    double["Bar"][2] = "Two"
    assert double["Bar"][2] == "Two"


def test_singleSet():
    matrix = DemoMatrix()
    double = DoubleDict(xtype=str, ytype=int, matrix=matrix)
    new_data = {1: "One", 2: "Two"}
    double["foo"] = new_data
    assert double["foo"][1] == "One"


def test_insert_inverted():
    matrix = DemoMatrix()
    matrix.set_data("Foo", 1, "One")
    double = DoubleDict(xtype=str, ytype=int, matrix=matrix)
    assert double[1]["Foo"] == "One"
    double[2]["Bar"] = "Two"
    assert double["Bar"][2] == "Two"
    assert double[2]["Bar"] == "Two"


def test_singleSet_inverted():
    matrix = DemoMatrix()
    double = DoubleDict(xtype=str, ytype=int, matrix=matrix)
    new_data = {"foo": "One", "bar": "Two"}
    double[1] = new_data
    assert double["foo"][1] == "One"
    assert double[1]["bar"] == "Two"
