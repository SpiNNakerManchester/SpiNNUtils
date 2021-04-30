# Copyright (c) 2018 The University of Manchester
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

import unittests
from spinn_utilities.helpful_functions import (
    get_valid_components, is_singleton, gcd, lcm, testing)


def test_is_singleton():
    assert is_singleton(35)
    assert is_singleton(False)
    assert is_singleton(0.12)
    assert is_singleton("")
    assert is_singleton('a')
    assert is_singleton("flashy fish")
    assert not is_singleton([1, 2, 3])
    assert not is_singleton({1: 2, 3: 4})
    assert not is_singleton(frozenset([14]))
    assert not is_singleton((43876,))
    assert is_singleton(object())
    assert is_singleton(lambda x: x * 2 + 1)


def test_get_valid_components():
    # WTF is this function doing?!
    d = get_valid_components(unittests.test_helpful_functions, "_c")
    assert len(d) == 3
    assert d['a'] == a_c
    assert d['a_b'] == a_b
    assert d['b'] == b_c


def test_gcd():
    assert gcd(2) == 2
    assert gcd(30, 40) == 10
    assert gcd(120, 40, 60) == 20
    a = [2, 3, 4]
    assert gcd(a) == 1
    b = set([1000, 500, 1500])
    assert gcd(b) == 500
    c = [34]
    assert gcd(c) == 34


def test_lcm():
    assert lcm(2) == 2
    assert lcm(30, 40) == 120
    assert lcm(120, 40, 60) == 120
    assert lcm() == 1
    assert lcm([]) == 1
    a = [2, 3, 4]
    assert lcm(a) == 12
    b = set([1000, 500, 1500])
    assert lcm(b) == 3000
    c = [34]
    assert lcm(c) == 34

def test_testing():
    assert (testing())


# Support class for test_get_valid_components
class a_b(object):  # noqa: N801
    pass


# Support class for test_get_valid_components
class b_c(object):  # noqa: N801
    pass


# Support class for test_get_valid_components
class a_c(object):  # noqa: N801
    pass
