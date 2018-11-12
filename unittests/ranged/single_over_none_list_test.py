from spinn_utilities.ranged import RangedList, SingleList


def test_simple():
    a_list = RangedList(5, [0, 1, 2, 3, 4], "many")
    single = SingleList(a_list=a_list, operation=lambda x: x + 5)
    assert single == [5, 6, 7, 8, 9]


def test_muliple():
    a_list = RangedList(5, [0, 1, 2, 3, 4], "many")
    q = 2
    single = SingleList(a_list=a_list, operation=lambda x: x * q)
    assert single == [0, 2, 4, 6, 8]
    a_list[1] = 6
    a_list[2] = 3.0
    a_list[3] = 8
    assert single == [0, 12, 6.0, 16, 8]


def create_lambda():
    import numpy
    machine_time_step = 1000
    return lambda x: numpy.exp(float(-machine_time_step) / (1000.0 * x))


def test_complex():
    a_list = RangedList(5, [2, 1, 2, 3, 4], "many")
    single = SingleList(a_list=a_list, operation=create_lambda())
    assert single == [0.60653065971263342, 0.36787944117144233,
                      0.60653065971263342, 0.716531310573789272,
                      0.77880078307140488]


def test_get_value():
    a_list = RangedList(5, [2, 1, 2, 3, 4], "many")
    single = SingleList(a_list=a_list, operation=create_lambda())
    assert single[2] == 0.60653065971263342


def test_apply_operation():
    a_list = RangedList(5, [2, 1, 2, 3, 4], "many")
    single = a_list.apply_operation(operation=create_lambda())
    assert single[2] == 0.60653065971263342


def test_get_slice():
    a_list = RangedList(5, [2, 1, 2, 3, 4], "many")
    single = SingleList(a_list=a_list, operation=lambda x: x + 3)
    a_list[1:3] = 6
    assert single[2:4] == [9, 6]


def test_ranges():
    a_list = RangedList(5, [0, 1, 2, 3, 4], "many")
    single = SingleList(a_list=a_list, operation=lambda x: x * 3)
    a_list[1:3] = 6
    assert [(0, 1, 0), (1, 3, 18), (3, 4, 9), (4, 5, 12)] == \
        list(single.iter_ranges())


def test_ranges_by_slice():
    a_list = RangedList(5, [0, 1, 2, 3, 4], "many")
    single = SingleList(a_list=a_list, operation=lambda x: x * 3)
    a_list[1:3] = 6
    assert [(2, 3, 18), (3, 4, 9)] == list(single.iter_ranges_by_slice(2, 4))


def test_get_ids():
    a_list = RangedList(5, [0, 1, 2, 3, 4], "many")
    single = SingleList(a_list=a_list, operation=lambda x: x * 3)
    assert single[1:5:2] == [3, 9]
    a_list[1:3] = 6
    assert single[1:5:2] == [18, 9]


def test_iter_by_slice():
    a_list = RangedList(5, [0, 1, 2, 3, 4], "many")
    single = SingleList(a_list=a_list, operation=lambda x: x + 10)
    assert [12, 13, 14] == list(single.iter_by_slice(2, 5))
    a_list[:3] = 6
    assert [16, 13, 14] == list(single.iter_by_slice(2, 5))
    a_list[4:] = 7
    assert [16, 13, 17] == list(single.iter_by_slice(2, 5))
