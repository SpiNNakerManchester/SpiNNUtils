# Copyright (c) 2017-2023 The University of Manchester
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

from spinn_utilities.matrix import DoubleDict, DemoMatrix


def test_insert():
    matrix = DemoMatrix()
    matrix.set_data("Foo", 1, "One")
    double = DoubleDict(xtype=str, ytype=int, matrix=matrix)
    assert double["Foo"][1] == "One"
    double["Bar"][2] = "Two"
    assert double["Bar"][2] == "Two"


def test_singleSet():
    matrix = DemoMatrix()
    double = DoubleDict(xtype=str, ytype=int, matrix=matrix)
    new_data = {1: "One", 2: "Two"}
    double["foo"] = new_data
    assert double["foo"][1] == "One"


def test_insert_inverted():
    matrix = DemoMatrix()
    matrix.set_data("Foo", 1, "One")
    double = DoubleDict(xtype=str, ytype=int, matrix=matrix)
    assert double[1]["Foo"] == "One"
    double[2]["Bar"] = "Two"
    assert double["Bar"][2] == "Two"
    assert double[2]["Bar"] == "Two"


def test_singleSet_inverted():
    matrix = DemoMatrix()
    double = DoubleDict(xtype=str, ytype=int, matrix=matrix)
    new_data = {"foo": "One", "bar": "Two"}
    double[1] = new_data
    assert double["foo"][1] == "One"
    assert double[1]["bar"] == "Two"


def test_errors():
    matrix = DemoMatrix()
    double = DoubleDict(xtype=str, ytype=int, matrix=matrix)
    new_data = {"foo": "One", "bar": "Two"}
    double[1] = new_data
    try:
        double[1.1]
        assert False
    except KeyError as ex:
        assert "unexpected type" in str(ex)
    try:
        double["Bar"] = "Opps"
    except ValueError as ex:
        assert "Value must of type dict" in str(ex)
    try:
        double["Bar"] = [2, "Opps"]
        assert False
    except ValueError as ex:
        assert "Value must of type dict" in str(ex)
    try:
        double["Bar"] = {2.1: "Opps"}
        assert False
    except ValueError as ex:
        assert "All keys in the value" in str(ex)
    try:
        double[2] = {1: "Opps"}
        assert False
    except ValueError as ex:
        assert "All keys in the value" in str(ex)
    try:
        double[2.1] = {1: "Opps"}
        assert False
    except KeyError as ex:
        assert "unexpected type" in str(ex)
