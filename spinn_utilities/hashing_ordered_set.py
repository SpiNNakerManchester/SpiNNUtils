from spinn_utilities.ordered_set import OrderedSet


class HashingOrderedSet(OrderedSet):
    """
    An Ordered set which provides LIMITED hash abilty

    These are hashed on ID not VALUE.

    Adding or removing elements will not change the hash key.

    BUT two sets that happen to have the same elemenets in the same order \
        which could be considered "equal" will NOT have the same hashkey!
    """

    def __hash__(self):
        """
        ID based haskkey.

        WARNING this breakes the general hash rule on equality\
            that if A == B hash(A) == hash(b)
        :return:
        """
        return id(self)
