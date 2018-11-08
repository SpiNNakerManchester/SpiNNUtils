import six


def as_string(bytestring, start=None, end=None):
    """
    Returns the length and the hex values.

    The length is always the full length irrespective of the start and end.

    :param bytestring: data as a bytestring
    :param start: the inclusive start of the slice to return. May be None
    :param end: the exclusive end of the slice to return. May be None
    :return: The length of the bytesting and the hex values, comma separated
    """
    return "(" + str(len(bytestring)) + ")" + as_hex(bytestring, start, end)


def as_hex(bytestring, start=None, end=None):
    """
    Returns the bytestring as string showing the hex values

    :param bytestring: data as a byteString
    :param start: the inclusive start of the slice to return. May be None
    :param end: the exclusive end of the slice to return. May be None
    :return: Comma separated hex values
    """
    return ','.join('%02x' % i for i in six.iterbytes(bytestring[start:end]))
