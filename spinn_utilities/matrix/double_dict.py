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

from typing import Generic, Mapping, Union, overload, cast
from .abstract_matrix import AbstractMatrix
from .x_view import XView
from .y_view import YView
from ._types import T, X, Y


class DoubleDict(Generic[T, X, Y]):
    __slots__ = [
        "_matrix", "_xtype", "_ytype"]

    def __init__(
            self, xtype: type[X], ytype: type[Y],
            matrix: AbstractMatrix[T, X, Y]):
        self._xtype = xtype
        self._ytype = ytype
        self._matrix = matrix

    @overload
    def __getitem__(self, key: X) -> XView[T, X, Y]:
        ...

    @overload
    def __getitem__(self, key: Y) -> YView[T, X, Y]:
        ...

    def __getitem__(self, key: Union[X, Y]) -> Union[
            XView[T, X, Y], YView[T, X, Y]]:
        if isinstance(key, self._xtype):
            return XView(x=key, matrix=self._matrix)
        if isinstance(key, self._ytype):
            return YView(y=key, matrix=self._matrix)
        raise KeyError(f"Key {key} has an unexpected type")

    @overload
    def __setitem__(self, key: X, value: Mapping[Y, T]):
        ...

    @overload
    def __setitem__(self, key: Y, value: Mapping[X, T]):
        ...

    def __setitem__(self, key: Union[X, Y],
                    value: Union[Mapping[X, T], Mapping[Y, T]]):
        try:
            if isinstance(key, self._xtype):
                correct = all(isinstance(y, self._ytype) for y in value.keys())
                if not correct:
                    raise ValueError(
                        f"All keys in the value must be of type {self._ytype}")
                val_y = cast(Mapping[Y, T], value)
                for y in val_y.keys():
                    self._matrix.set_data(x=key, y=y, value=val_y[y])
            elif isinstance(key, self._ytype):
                correct = all(isinstance(x, self._xtype) for x in value.keys())
                if not correct:
                    raise ValueError(
                        f"All keys in the value must be of type {self._xtype}")
                val_x = cast(Mapping[X, T], value)
                for x in val_x.keys():
                    self._matrix.set_data(x=x, y=key, value=val_x[x])
            else:
                raise KeyError(f"Key {key} has an unexpected type")
        except AttributeError as e:
            raise ValueError("Value must of type dict. Or at least "
                             "implement keys() and __getitem__") from e
