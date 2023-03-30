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

from .x_view import XView
from .y_view import YView


class DoubleDict(object):
    __slots__ = [
        "_matrix", "_xtype", "_ytype"]

    def __init__(self, xtype, ytype, matrix):
        self._xtype = xtype
        self._ytype = ytype
        self._matrix = matrix

    def __getitem__(self, key):
        if isinstance(key, self._xtype):
            return XView(x=key, matrix=self._matrix)
        if isinstance(key, self._ytype):
            return YView(y=key, matrix=self._matrix)
        raise KeyError(f"Key {key} has an unexpected type")

    def __setitem__(self, key, value):
        try:
            if isinstance(key, self._xtype):
                correct = all(isinstance(y, self._ytype) for y in value.keys())
                if not correct:
                    raise ValueError(
                        f"All keys in the value must be of type {self._ytype}")
                for y in value.keys():
                    self._matrix.set_data(x=key, y=y, value=value[y])
            elif isinstance(key, self._ytype):
                correct = all(isinstance(x, self._xtype) for x in value.keys())
                if not correct:
                    raise ValueError(
                        f"All keys in the value must be of type {self._xtype}")
                for x in value.keys():
                    self._matrix.set_data(x=x, y=key, value=value[x])
            else:
                raise KeyError(f"Key {key} has an unexpected type")
        except AttributeError as e:
            raise ValueError("Value must of type dict. Or at least "
                             "implement keys() and __getitem__") from e
