class Compare(object):
    """
    Test class
    """

    def return_good(self) -> int:
        """
        :return: the number 1
        """
        return 1

    def return_bad(self) -> int:
        """
        There should be a return tag
        """
        return 1

    def return_best(self) -> int:
        """
        Having a short description is nice but not required
        :return: the number 1
        """
        return 1

    @property
    def property_bad1(self) -> int:
        """
        :return: Having just a return on properties is ugly
        """
        return 2

    @property
    def property_bad2(self) -> int:
        """
        short description

        :return: Having a return even with a description is ugly
        """
        return 3

    @property
    def property_best1(self) -> int:
        """
        Just a description reads the cleanest
        """
        return 4

    @property
    def property_best2(self) -> int:
        """
        Just a description reads the cleanest

        Settable
        """
        return 5

    @property_best1.setter
    def property_good2(self, a: int) -> None:
        """
        Docs on setters are ignored
        """
        print(a)

    def params_best1(self, x:int, y:int, label:str) -> None:
        """
        Having a short description is needed if no return

        :param x: chip x
        :param y: chip y
        :param label: name of vertex
        """
        print(x, y, label)

    def params_best2(self, x: int, y: int, label: str) -> str:
        """
        Having a short description is best even with a return

        :param x: chip x
        :param y: chip y
        :param label:  name of vertex
        :return: Return description
        """
        return f"{label} on {x}:{y}"

    def params_good(self, x: int, y: int, label: str) -> str:
        """
        :param x: chip x
        :param y: chip y
        :param label:  name of vertex
        :return: Just a return description is still good
        """
        return f"{label} on {x}:{y}"

    def params_ok1(self, x:int, y:int, label:str) -> None:
        """
        Having just some params with text is ok

        :param x:
        :param y:
        :param label:  name of vertex
        """
        print(x, y, label)

    def params_ok2(self, x:int, y:int, label:str) -> None:
        """
        Having no params is ok
        """
        print(x, y, label)

    def params_acceptable(self, x:int, y:int, label:str) -> None:
        """
        Having just all params empty is weird not wrong

        :param x:
        :param y:
        :param label:
        """
        print(x, y, label)

    def params_bad1(self, x:int, y:int, label:str) -> None:
        """
        Having just some params is bad even with text

        :param label:  name of vertex
        """
        print(x, y, label)

    def params_bad2(self, x:int, y:int, label:str) -> None:
        """
        Having just some params with no text is worst

        :param label:
        """
        print(x, y, label)


class InInit(object):
    """
    The params are in the init method docs
    """

    def __init__(self, x: int, y: int, label: str):
        """
        :param x: chip x
        :param y: chip y
        :param label:  name of vertex
        """
        print(x, y, label)


class InClass(object):
    """
    The params are in the class docs

    :param x: chip x
    :param y: chip y
    :param label:  name of vertex
    """

    def __init__(self, x: int, y: int, label: str):
        print(x, y, label)