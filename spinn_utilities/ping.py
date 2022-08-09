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
    def ping(ipaddr):
        """
        Send a ping (ICMP ECHO request) to the given host.
        SpiNNaker boards support ICMP ECHO when booted.

        :param str ipaddr:
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
            cmd + ipaddr, shell=True, stdout=subprocess.PIPE)
        time.sleep(1.2)
        process.stdout.close()
        process.wait()
        return process.returncode

    @staticmethod
    def host_is_reachable(ipaddr):
        """
        Test if a host is unreachable via ICMP ECHO. Note that this caches.

        :param str ipaddr:
            The IP address to ping. Hostnames can be used, but are not
            recommended.
        :rtype: bool
        """
        if ipaddr in Ping.unreachable:
            return False
        tries = 0
        while (True):
            if Ping.ping(ipaddr) == 0:
                return True
            tries += 1
            if tries > 10:
                Ping.unreachable.add(ipaddr)
                return False
