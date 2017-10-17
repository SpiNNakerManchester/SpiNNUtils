class MultipleValuesException(Exception):

    def __init__(self, key=None, value1=None, value2=None):
        if key is None:
            msg = "Multiple values found"
        else:
            msg = "Multiple values found for key {}".format(key)
        if not value1 is None and not value2 is None:
            msg += " values found include {} and {}".format(value1, value2)
        Exception.__init__(msg)