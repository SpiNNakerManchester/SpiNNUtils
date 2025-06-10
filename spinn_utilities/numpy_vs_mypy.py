# Copyright (c) 2025 The University of Manchester
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

from typing import List
import numpy
from numpy.typing import NDArray

int_list: List[int] = [0, 1, 2]
int_array: NDArray[numpy.integer] = numpy.array(int_list, dtype=numpy.int32)
float_array: NDArray[numpy.floating] = numpy.array([1, 2, 3], dtype=numpy.float32)
print(int_array)
for i in int_array:
    print(float_array[i])
for i in int_array:
    print(float(float_array[i]))
    print(max(float_array[i], 1.5))
