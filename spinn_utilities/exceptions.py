

class SpiNNUtilsException(Exception):
    """ Superclass of all exceptions from the SpiNNUtils module.
    """


class FailedToFindBinaryException(SpiNNUtilsException):
    """ Raised when the executable finder cant find the binary
    """
