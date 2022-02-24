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

from spinn_utilities.config_holder import get_config_int, get_config_str


class SocketAddress(object):
    """ Data holder for a socket interface for notification protocol.
    """
    __slots__ = [
        "_listen_port",
        "_notify_host_name",
        "_notify_port_no",
        "__hash"]

    def __init__(self, notify_host_name=None, notify_port_no=None,
                 listen_port=None):
        """
        :param notify_host_name:
            Host to talk to tell that the database (and application) is ready.
        :type notify_host_name: str or None
        :param notify_port_no:
            Port to talk to tell that the database (and application) is ready.
        :type notify_port_no: int or None
        :param listen_port:
            Port on which to listen for an acknowledgement that the
            simulation should start.
        :type listen_port: int or None
        """
        if notify_port_no is None:
            notify_port_no = get_config_int("Database", "notify_port")
        else:
            notify_port_no = int(notify_port_no)
        if notify_host_name is None:
            notify_host_name = get_config_str("Database", "notify_hostname")
        elif notify_host_name == "0.0.0.0":
            notify_host_name = "localhost"
        else:
            notify_host_name = str(notify_host_name)
        if listen_port is None:
            listen_port = get_config_int("Database", "listen_port")
        else:
            listen_port = int(listen_port)
        self._notify_host_name = notify_host_name
        self._notify_port_no = notify_port_no
        self._listen_port = listen_port
        self.__hash = None

    @property
    def notify_host_name(self):
        """ The notify host name
        """
        return self._notify_host_name

    @property
    def notify_port_no(self):
        """ The notify port no
        """
        return self._notify_port_no

    @property
    def listen_port(self):
        """ The port to listen to for responses
        """
        return self._listen_port

    def __eq__(self, other):
        if not isinstance(other, SocketAddress):
            return False
        return (self._notify_host_name == other.notify_host_name and
                self._notify_port_no == other.notify_port_no and
                self._listen_port == other.listen_port)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        if self.__hash is None:
            self.__hash = hash((self._listen_port, self._notify_host_name,
                                self._notify_port_no))
        return self.__hash

    def __repr__(self):
        return "SocketAddress({}, {}, {})".format(
            repr(self._notify_host_name), self._notify_port_no,
            self._listen_port)
