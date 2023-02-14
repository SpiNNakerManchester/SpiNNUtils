# Copyright (c) 2017-2018 The University of Manchester
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


class YView(object):
    """ A view along a particular y-slice of a 2D matrix.
    """
    __slots__ = [
        "_matrix", "_y"]

    def __init__(self, y, matrix):
        self._y = y
        self._matrix = matrix

    def __getitem__(self, key):
        return self._matrix.get_data(x=key, y=self._y)

    def __setitem__(self, key, value):
        self._matrix.set_data(x=key, y=self._y, value=value)
