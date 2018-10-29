def as_string(bytestring):
    """
    Retruns the length an dthe hexs values

    :param bytestring: data as a byteString
    :return: The length of the bytesting and the hex valies comma seperated
    """
    return "(" + str(len(bytestring)) + ")" + as_hex(bytestring)


def as_hex(bytestring):
    """
    Returns the bytestring as String showing the hex values

    :param bytestring: data as a byteString
    :return: Comma seperated hex values
    """

    return ','.join('{:02x}'.format(x) for x in bytestring)
