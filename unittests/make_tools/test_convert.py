import os
import sys
import unittest

from spinn_utilities.make_tools.converter import Converter
import spinn_utilities.make_tools.converter as converter


class TestConverter(unittest.TestCase):

    def setUp(self):
        class_file = sys.modules[self.__module__].__file__
        path = os.path.dirname(os.path.abspath(class_file))
        os.chdir(path)
        converter.RANGE_DIR = ""

    def test_convert(self):
        src = "mock_src"
        dest = "modified_src"
        dict = os.path.join("modified_src", "test.dict")
        Converter.convert(src, dest, dict)

    def test_convert_ranged(self):
        src = "mock_src"
        dest = "modified_src"
        dict = os.path.join("modified_src", "test.dict")
        Converter.convert(src, dest, dict)
        dict = os.path.join("modified_src", "test2.dict")
        Converter.convert(src, dest, dict)