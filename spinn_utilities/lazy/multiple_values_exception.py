class MultipleValuesException(Exception):

    def __init__(self):
        Exception.__init__("Multiple values found")