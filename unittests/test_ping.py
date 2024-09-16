# Copyright (c) 2018 The University of Manchester
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
import os
import pytest
from spinn_utilities.ping import Ping

skip_ping_tests = pytest.mark.skipif(
    (os.getenv("SKIP_PING_TESTS", "false") == "true"),
    reason="No remote ICMP ECHO in Github Actions")


@skip_ping_tests
def test_spalloc():
    # Should be able to reach Spalloc...
    assert Ping.host_is_reachable("spinnaker.cs.man.ac.uk")


@skip_ping_tests
def test_google_dns():
    # *REALLY* should be able to reach Google's DNS..
    assert Ping.host_is_reachable("8.8.8.8")


def test_localhost():
    # Can't ping localhost? Network catastrophically bad!
    assert Ping.host_is_reachable("localhost")


def test_ping_down_host():
    # Definitely unpingable host
    assert not Ping.host_is_reachable("169.254.254.254")
