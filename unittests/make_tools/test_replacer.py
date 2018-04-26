import unittest
from spinn_utilities.make_tools.replacer import Replacer
from spinn_utilities.make_tools.file_convertor import TOKEN


class TestReplacer(unittest.TestCase):

    def test_replacer(self):
        replacer = Replacer("test.aplx")
        new = replacer.replace("1001")
        assert ("[INFO] (weird;file.c: 9): this is ok" == new)

    def test_not_there(self):
        replacer = Replacer("not_there.pointer")
        assert ("1001" == replacer.replace("1001"))

    def test_not_extension(self):
        replacer = Replacer("test")
        new = replacer.replace("1014" + TOKEN + "123")
        assert ("[INFO] (weird;file.c: 47): second 123" == new)
