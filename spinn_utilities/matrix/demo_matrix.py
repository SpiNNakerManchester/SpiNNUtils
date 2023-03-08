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
from spinn_utilities.overrides import overrides
from .abstract_matrix import AbstractMatrix


class DemoMatrix(AbstractMatrix):
    __slots__ = [
        "data"]

    def __init__(self):
        self.data = defaultdict(dict)

    @overrides(AbstractMatrix.get_data)
    def get_data(self, x, y):
        return self.data[x][y]

    @overrides(AbstractMatrix.set_data)
    def set_data(self, x, y, value):
        self.data[x][y] = value
