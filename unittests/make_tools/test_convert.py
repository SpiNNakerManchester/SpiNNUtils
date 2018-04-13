import os
import unittest

from spinn_utilities.make_tools.convertor import Convertor
import spinn_utilities.make_tools.convertor as convertor


class TestConvertor(unittest.TestCase):

    def test_convert(self):
        src = "mock_src"
        dest = "modified_src"
        dict = os.path.join("modified_src", "test.dict")
        Convertor.convert(src, dest, dict)

    def test_convert_ranged(self):
        src = "mock_src"
        dest = "modified_src"
        dict = os.path.join("modified_src", "test.dict")
        convertor.RANGE_FILE = "test_ranges.txt"
        Convertor.convert(src, dest, dict, "test_one")
        dict = os.path.join("modified_src", "test2.dict")
        Convertor.convert(src, dest, dict, "test_two")

