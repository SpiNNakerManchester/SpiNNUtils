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

import platform
import subprocess
import time


class Ping(object):
    """
    Platform-independent ping support.
    """

    #: The unreachable host cache.
    unreachable = set()

    @staticmethod
    def ping(ip_address):
        """
        Send a ping (ICMP ECHO request) to the given host.
        SpiNNaker boards support ICMP ECHO when booted.

        :param str ip_address:
            The IP address to ping. Hostnames can be used, but are not
            recommended.
        :return:
            return code of subprocess; 0 for success, anything else for failure
        :rtype: int
        """
        if platform.platform().lower().startswith("windows"):
            cmd = "ping -n 1 -w 1 "
        else:
            cmd = "ping -c 1 -W 1 "
        process = subprocess.Popen(
            cmd + ip_address, shell=True, stdout=subprocess.PIPE)
        time.sleep(1.2)
        process.stdout.close()
        process.wait()
        return process.returncode

    @staticmethod
    def host_is_reachable(ip_address):
        """
        Test if a host is unreachable via ICMP ECHO.

        .. note::
            This information may be cached in various ways. Transient failures
            are not necessarily detected or recovered from.

        :param str ip_address:
            The IP address to ping. Hostnames can be used, but are not
            recommended.
        :rtype: bool
        """
        if ip_address in Ping.unreachable:
            return False
        tries = 0
        while (True):
            if Ping.ping(ip_address) == 0:
                return True
            tries += 1
            if tries > 10:
                Ping.unreachable.add(ip_address)
                return False
