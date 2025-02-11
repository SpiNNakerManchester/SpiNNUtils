# Copyright (c) 2018 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from spinn_utilities.helpful_functions import (is_singleton, gcd, lcm)


def test_is_singleton() -> None:
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


def test_gcd() -> None:
    assert gcd(2) == 2
    assert gcd(30, 40) == 10
    assert gcd(120, 40, 60) == 20
    a = [2, 3, 4]
    assert gcd(a) == 1
    b = set([1000, 500, 1500])
    assert gcd(b) == 500
    c = [34]
    assert gcd(c) == 34


def test_lcm() -> None:
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
