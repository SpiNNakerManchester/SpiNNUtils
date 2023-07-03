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

from collections import defaultdict
from typing import Dict, Generic
from spinn_utilities.overrides import overrides
from .abstract_matrix import AbstractMatrix
from ._types import T, X, Y


class DemoMatrix(AbstractMatrix[T, X, Y], Generic[T, X, Y]):
    __slots__ = (
        "data")

    def __init__(self) -> None:
        self.data: Dict[X, Dict[Y, T]] = defaultdict(dict)

    @overrides(AbstractMatrix.get_data)
    def get_data(self, x: X, y: Y) -> T:
        return self.data[x][y]

    @overrides(AbstractMatrix.set_data)
    def set_data(self, x: X, y: Y, value: T):
        self.data[x][y] = value
