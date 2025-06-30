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

    def doc_param(self, foo:int) -> None:
        """
        :param foo: The funny odd object to set
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
