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

from spinn_utilities.matrix.demo_matrix import DemoMatrix


def test_insert():
    matrix = DemoMatrix()
    matrix.set_data("Foo", 1, "One")
    test = matrix.data["Foo"]
    assert "One" == test[1]
    assert "One" == matrix.get_data("Foo", 1)
