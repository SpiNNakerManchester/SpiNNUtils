import os
import unittest

from unittests.make_tools.test_convert import TestConvertor
from spinn_utilities.make_tools.replacer import Replacer


class TestReplacer(unittest.TestCase):

    def setUp(self):
        global replacer
        convert_dir = os.path.dirname(os.path.abspath(__file__))
        replacer = Replacer(convert_dir)

    def test_replace_simple(self):
        replacement = replacer.replace("9001")
        assert "[INFO] (weird;file.c: 9): this is ok\n" == replacement

    def test_replace_two(self):
        replacement = replacer.replace("9007 123 456")
        assert "[INFO] (weird;file.c: 29): \\t back off = 123, time between " \
            "spikes 456\n" == replacement
