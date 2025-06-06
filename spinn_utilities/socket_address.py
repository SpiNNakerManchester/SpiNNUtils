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

from typing import Any, Optional
from spinn_utilities.config_holder import (
    get_config_int, get_config_int_or_none, get_config_str)


class SocketAddress(object):
    """
    Data holder for a socket interface for notification protocol.
    """
    __slots__ = [
        "_listen_port",
        "_notify_host_name",
        "_notify_port_no",
        "__hash"]

    def __init__(self, notify_host_name: Optional[str] = None,
                 notify_port_no: Optional[int] = None,
                 listen_port: Optional[int] = None):
        """
        :param notify_host_name:
            Host to talk to tell that the database (and application) is ready.
        :param notify_port_no:
            Port to talk to tell that the database (and application) is ready.
        :param listen_port:
            Port on which to listen for an acknowledgement that the
            simulation should start.
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
            listen_port = get_config_int_or_none("Database", "listen_port")
        else:
            listen_port = int(listen_port)
        self._notify_host_name = notify_host_name
        self._notify_port_no = notify_port_no
        self._listen_port = listen_port
        self.__hash: Optional[int] = None

    @property
    def notify_host_name(self) -> str:
        """
        The host name or IP address to send a notification message to.
        """
        return self._notify_host_name

    @property
    def notify_port_no(self) -> int:
        """
        The UDP port number to send a notification message to.
        """
        return self._notify_port_no

    @property
    def listen_port(self) -> Optional[int]:
        """
        The port to listen to for responses.
        """
        return self._listen_port

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SocketAddress):
            return False
        return (self._notify_host_name == other.notify_host_name and
                self._notify_port_no == other.notify_port_no and
                self._listen_port == other.listen_port)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        if self.__hash is None:
            self.__hash = hash((self._listen_port, self._notify_host_name,
                                self._notify_port_no))
        return self.__hash

    def __repr__(self) -> str:
        return (f"SocketAddress({repr(self._notify_host_name)}, "
                f"{self._notify_port_no}, {self._listen_port})")
