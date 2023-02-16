# Copyright (c) 2017 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from .abstract_has_constraints import AbstractHasConstraints
from .abstract_has_label import AbstractHasLabel
from .abstract_has_id import AbstractHasId
from .grandparent import GrandParent
from .no_label import NoLabel
from .unchecked_bad_param import UncheckedBadParam


def test_create():
    o = GrandParent()
    assert o is not None
    assert isinstance(o, AbstractHasLabel)
    assert isinstance(o, AbstractHasConstraints)
    assert isinstance(o, GrandParent)
    assert not isinstance(o, AbstractHasId)


def test_no_has_label():
    with pytest.raises(TypeError):
        NoLabel()


# What this test checks is actually undesirable but it shows it happens
def test_unchecked_bad_param():
    o = UncheckedBadParam()
    assert o is not None


def test_checked_bad_param():
    with pytest.raises(AttributeError):
        from .checked_bad_param import CheckedBadParam
        # This line never reached but there for pep8
        CheckedBadParam()
