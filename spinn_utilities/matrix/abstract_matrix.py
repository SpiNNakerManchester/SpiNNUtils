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

from spinn_utilities.abstract_base import AbstractBase, abstractmethod


class AbstractMatrix(object, metaclass=AbstractBase):
    """
    A rectangular 2D collection of data.
    """
    __slots__ = []

    @abstractmethod
    def get_data(self, x, y):
        """
        Get the value at a particular X,Y coordinate.
        """

    @abstractmethod
    def set_data(self, x, y, value):
        """
        Set the value at a particular X,Y coordinate.
        """
