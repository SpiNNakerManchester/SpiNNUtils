class SocketAddress(object):
    """ Data holder for a socket interface for notification protocol.
    """
    __slots__ = [
        "_listen_port",
        "_notify_host_name",
        "_notify_port_no",
        "__hash"]

    def __init__(self, notify_host_name, notify_port_no, listen_port):
        self._notify_host_name = str(notify_host_name)
        self._notify_port_no = int(notify_port_no)
        self._listen_port = (
            listen_port if listen_port is None else int(listen_port))
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
            self._notify_host_name.__repr__(), self._notify_port_no,
            self._listen_port)
