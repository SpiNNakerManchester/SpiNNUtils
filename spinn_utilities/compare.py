class Compare(object):

    def short_description(self, foo:int) -> None:
        """
        Sets funny odd object
        """
        self.foo = foo

    def doc_param(self, foo:int) -> None:
        """
        :param foo: The funny odd object to set
        """
        self.foo = foo

    @property
    def foo(self) -> int:
        """
        :return: The funny odd object - property
        """
        return self.foo

    @foo.setter
    def foo(self, foo: int):
        """
        Sets funny odd object - setter
        """
        self.foo = foo