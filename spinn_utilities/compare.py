class Compare(object):

    def setter_doced(self, foo:int) -> None:
        """
        Sets funny odd object
        """
        self.foo = foo

    def setter_param(self, foo:int) -> None:
        """
        :param foo: funny even object to set to foo
        """
        self.foo = foo

    def return_doced(self) -> int:
        """
        :return: the number 1
        """
        return 1

    def return_description(self) -> int:
        """
        the number 1
        """
        return 1

    @property
    def foo(self) -> int:
        """
        :return: The fancy old orange
        """
        return self.foo

    @foo.setter
    def foo(self, foo: int):
        """
        Sets fancy old orange
        """
        self.foo = foo

    @property
    def bar(self) -> int:
        """
        The basic alpha ram
        """
        return self.bar

    def params_none(self, a:int, b:float, c:str) -> bool:
        """
        No parameters listed

        :return: True
        """
        print(a, b, c)
        return True

    def params_all(self, a: int, b: float, c: str) -> bool:
        """
        all parameters listed

        :param a:
        :param b:
        :param c:
        :return: True
        """
        print(a, b, c)
        return True

    def params_some(self, a: int, b: float, c: str) -> bool:
        """
        all parameters listed

        :param a:
        :param c:
        :return: True
        """
        print(a, b, c)
        return True