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
    Tests for ICMP host reachability.

    .. note::
        A properly booted SpiNNaker machine is guaranteed to respond to ICMP
        ECHO requests.

    .. warning::
        These tests are able to fail in several ways. In particular, some ISPs
        make hosts appear to be reachable even when they are not, and some
        environments (such as Azure, used by Github Actions) make hosts appear
        unreachable even when actually connecting to them with TCP or UDP will
        work. These are fundamental limitations relating to host resolution
        and firewalls.
    """
    _unreachable = set()
    _MAX_TRIES = 10

    @staticmethod
    def ping(ipaddr):
        """
        Wrapper around the system ``ping`` program.

        :param str ipaddr:
            The IP address (or host name) of the machine to ping.
        :return: The program exit code.
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

    @classmethod
    def host_is_reachable(cls, ipaddr):
        """
        Wrapper for :py:meth:`ping` that converts numeric results into a
        reachability decision, retries a few times in case a temporary network
        glitch is occurring, and caches (slow) unreachability results.

        :param str ipaddr:
            The IP address (or host name) of the machine to ping.
        :return: ``True`` if the machine is reachable.
        :rtype: bool
        """
        if ipaddr in cls._unreachable:
            return False
        for _try in range(cls._MAX_TRIES):
            if cls.ping(ipaddr) == 0:
                return True
        cls._unreachable.add(ipaddr)
        return False
