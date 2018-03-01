import pytest
from spinn_utilities.ordered_set import OrderedSet


def test_create():
    o = OrderedSet()
    assert o is not None


def test_set_ness():
    o = OrderedSet()
    assert len(o) == 0
    o.add(123)
    assert len(o) == 1
    o.add(123)
    assert len(o) == 1
    o.add(456)
    assert len(o) == 2
    o.add(456)
    assert len(o) == 2
    o.add(123)
    assert len(o) == 2
    assert o == set([123, 456])
    assert o == set([456, 123])
    assert o == [123, 456]
    assert o == [456, 123]
    o.remove(123)
    assert len(o) == 1
    o.remove(456)
    assert len(o) == 0
    with pytest.raises(KeyError):  # @UndefinedVariable
        o.remove(789)
    o.discard(789)
    assert len(o) == 0
    o.add(789)
    assert len(o) == 1
    assert 789 in o
    o.discard(789)
    assert 789 not in o
    assert len(o) == 0


def test_ordered_ness():
    o = OrderedSet()
    o.add(12)
    o.add(78)
    o.add(56)
    o.add(34)
    o.add(90)
    assert len(o) == 5
    assert list(o) == [12, 78, 56, 34, 90]
    result = []
    for item in o:
        result.append(item)
    assert result == [12, 78, 56, 34, 90]


def test_containment():
    o = OrderedSet()
    o.add(12)
    o.add(78)
    o.add(56)
    o.add(34)
    o.add(90)
    for item in [12, 78, 56, 34, 90]:
        assert item in o
    for item in [123, 456, 789]:
        assert item not in o


def test_repr():
    o = OrderedSet()
    o.add(12)
    o.add(78)
    o.add(56)
    o.add(34)
    o.add(90)
    s = "{}".format(o)
    assert s == "OrderedSet([12, 78, 56, 34, 90])"


def test_pop():
    o = OrderedSet()
    o.add(12)
    o.add(78)
    o.add(56)
    o.add(34)
    o.add(90)
    for item in [90, 34, 56, 78, 12]:
        assert o.pop() == item
    with pytest.raises(KeyError):  # @UndefinedVariable
        o.pop()


def test_update():
    o = OrderedSet()
    o.add(1)
    o.add(2)
    o.add(3)
    o.update([3, 4, 5])
    for item in (5, 4, 3, 2, 1):
        print("o={}".format(repr(o)))
        assert o.pop() == item
    with pytest.raises(KeyError):
        o.pop()


def test_obscure_stuff():
    o = OrderedSet()
    o.add(1)
    o.add(2)
    o.add(3)
    assert [x for x in reversed(o)] == [3, 2, 1]
    o2 = OrderedSet(o)
    assert [x for x in o2] == [1, 2, 3]
    assert o == o2
    o2 |= [4]
    assert o != o2
    assert repr(OrderedSet()) == "OrderedSet()"
