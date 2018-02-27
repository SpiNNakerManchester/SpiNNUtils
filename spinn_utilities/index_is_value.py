import sys


class IndexIsValue(object):
    """ Tiny support class that implements ``object[x]`` by just returning\
        ``x`` itself.

    Used for where you want a range from 1 to *N* but you don't know *N*.

    Clearly, operations that assume a finite list are *not* supported.
    """

    def __getitem__(self, key):
        return key

    def __len__(self):
        return sys.maxint
