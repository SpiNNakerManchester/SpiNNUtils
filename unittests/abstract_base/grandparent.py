# Copyright (c) 2017 The University of Manchester
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

from typing import Any
from spinn_utilities.overrides import overrides
from .abstract_grandparent import AbstractGrandParent
from .abstract_has_constraints import AbstractHasConstraints


class GrandParent(AbstractGrandParent):

    def label(self):
        return "GRANDPARENT"

    def set_label(selfself, label):
        pass

    @overrides(AbstractHasConstraints.add_constraint)
    def add_constraint(self, constraint: Any):
        raise NotImplementedError("We set our own constrainst")

    @overrides(AbstractHasConstraints.constraints)
    def constraints(self) -> Any:
        return ["No night feeds", "No nappy changes"]
