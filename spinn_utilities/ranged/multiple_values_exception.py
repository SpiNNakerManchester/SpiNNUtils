class MultipleValuesException(Exception):

    def __init__(self, key=None, value1=None, value2=None):
        if key is None:
            msg = "Multiple values found"
        else:
            msg = "Multiple values found for key {}".format(key)
        if value1 is not None and value2 is not None:
            msg += " values found include {} and {}".format(value1, value2)
        super(MultipleValuesException, self).__init__(msg)
