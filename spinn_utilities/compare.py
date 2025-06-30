class Compare(object):

    def short_description_setter(self, foo:int) -> None:
        """
        Sets funny odd object
        """
        self.foo = foo

    def doc_param(self, foo:int) -> None:
        """
        :param foo: The funny odd object to set
        """
        self.foo = foo

    def doc_return(self) -> int:
        """
        :return: the number 1
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

    @bar.setter
    def bar(self, bar: int):
        """
        Sets basic alpha ram
        """
        self.bar = bar

    @property
    def no_setter(self) -> int:
        """
        :return: The first number
        """
        return 1

