# Copyright (c) 2020 The University of Manchester
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

from spinn_utilities.abstract_context_manager import AbstractContextManager


class CM(AbstractContextManager):
    def __init__(self):
        self.state = None

    def _context_entered(self):
        self.state = 0

    def close(self):
        self.state += 1

    def _context_exception_occurred(self, exc_type, exc_val, exc_tb):
        self.state = str(exc_val)


class CMTestExn(Exception):
    """ Just an exception different from all others for testing. """


def test_acm_with_success():
    states = []
    cm = CM()
    states.append(cm.state)
    with cm:
        states.append(cm.state)
    states.append(cm.state)
    assert states == [None, 0, 1]


def test_acm_with_exception():
    states = []
    cm = CM()
    try:
        states.append(cm.state)
        with cm:
            states.append(cm.state)
            raise CMTestExn("boo")
    except CMTestExn:
        pass
    states.append(cm.state)
    assert states == [None, 0, "boo"]
