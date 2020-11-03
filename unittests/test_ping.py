# Copyright (c) 2018 The University of Manchester
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

from spinn_utilities.ping import Ping

"""
def test_spalloc():
    # Should be able to reach Spalloc...
    assert(Ping.host_is_reachable("spinnaker.cs.man.ac.uk"))


def test_google_dns():
    # *REALLY* should be able to reach Google's DNS..
    assert(Ping.host_is_reachable("8.8.8.8"))
"""


def test_localhost():
    # Can't ping localhost? Network catastrophically bad!
    assert(Ping.host_is_reachable("localhost"))


def test_ping_down_host():
    # Definitely unpingable host
    assert(not Ping.host_is_reachable("169.254.254.254"))
