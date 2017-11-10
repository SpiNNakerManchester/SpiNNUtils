from spinn_utilities.matrix.demo_matrix import DemoMatrix


def test_insert():
    matrix = DemoMatrix()
    matrix.set_data("Foo", 1, "One")
    test = matrix.data["Foo"]
    assert "One" == test[1]
    assert "One" == matrix.get_data("Foo", 1)
