from spinn_utilities.ranged.ranged_list import RangedList
from spinn_utilities.ranged.single_list import SingleList

def test_simple():
    a_list = RangedList(5, 12, "twelve")
    single = SingleList(a_list=a_list, operation=lambda x: x + 5)
    assert list(single) == [17, 17, 17, 17, 17]


def test_muliple():
    a_list = RangedList(5, 12, "twelve")
    q = 2
    single = SingleList(a_list=a_list, operation=lambda x: x / q)
    assert list(single) == [6, 6, 6, 6, 6]
    a_list[1] = 6
    a_list[2] = 3.0
    a_list[3] = 8
    assert list(single) == [6, 3, 1.5, 4, 6]


def create_lambda():
    import numpy
    machine_time_step = 1000
    return lambda x: numpy.exp(float(-machine_time_step) / (1000.0 * x))


def test_complex():
    a_list = RangedList(5, 20, "twelve")
    single = SingleList(a_list=a_list, operation=create_lambda())
    assert list(single) == [0.95122942450071402, 0.95122942450071402,
                            0.95122942450071402, 0.95122942450071402,
                            0.95122942450071402]


def test_get_value():
    a_list = RangedList(5, 20, "twelve")
    single = SingleList(a_list=a_list, operation=create_lambda())
    assert single[2] == 0.95122942450071402


def test_apply_operation():
    a_list = RangedList(5, 20, "twelve")
    single = a_list.apply_operation(operation=create_lambda())
    assert single[2] == 0.95122942450071402


def test_get_slice():
    a_list = RangedList(5, 12, "twelve")
    single = SingleList(a_list=a_list, operation=lambda x: x / 3)
    a_list[1:3] = 6
    assert single[2:4] == [2, 4]


def test_ranges():
    a_list = RangedList(5, 12, "twelve")
    single = SingleList(a_list=a_list, operation=lambda x: x / 3)
    a_list[1:3] = 6
    assert [(0, 1, 4), (1, 3, 2), (3, 5, 4)] == list(single.iter_ranges())


def test_ranges_by_slice():
    a_list = RangedList(5, 12, "twelve")
    single = SingleList(a_list=a_list, operation=lambda x: x / 3)
    a_list[1:3] = 6
    assert [(2, 3, 2), (3, 4, 4)] == list(single.iter_ranges_by_slice(2, 4))


def test_get_ids():
    a_list = RangedList(5, 12, "twelve")
    single = SingleList(a_list=a_list, operation=lambda x: x / 3)
    assert single[1:5:2] == [4, 4]
    a_list[1:3] = 6
    assert single[1:5:2] == [2, 4]
