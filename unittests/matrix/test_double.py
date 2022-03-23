# Copyright (c) 2017-2018 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
