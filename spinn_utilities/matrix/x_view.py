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
from typing import Generic
from .abstract_matrix import AbstractMatrix
from ._types import T, X, Y


class XView(Generic[T, X, Y]):
    """
    A view along a particular x-slice of a 2D matrix.
    """
    __slots__ = ("_matrix", "_x")

    def __init__(self, x: X, matrix: AbstractMatrix[T, X, Y]):
        self._x = x
        self._matrix = matrix

    def __getitem__(self, key: Y) -> T:
        return self._matrix.get_data(x=self._x, y=key)

    def __setitem__(self, key: Y, value: T):
        self._matrix.set_data(x=self._x, y=key, value=value)
