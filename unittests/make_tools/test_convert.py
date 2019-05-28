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

    def test_replace(self):
        src = "mock_src"
        dest = "modified_src"
        dict = os.path.join("modified_src", "test.dict")
        c = Converter(src, dest, dict)
        path = "/home/me/mock_src/FEC/c_common/fec/mock_src/"
        new_path = "/home/me/mock_src/FEC/c_common/fec/modified_src/"
        self.assertEqual(new_path, c._any_destination(path))

    def test_double_level(self):
        cwd = os.getcwd()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        weird_dir = os.path.join(dir_path, "foo", "bar")
        os.chdir(weird_dir)
        src = "foo/"
        dest = "bar/"
        dict = os.path.join("bar", "test.dict")
        c = Converter(src, dest, dict)
        c.run()
        weird_dir = os.path.join(dir_path, "foo", "bar", "gamma")
        os.chdir(weird_dir)
        dict = os.path.join("bar", "test.dict")
        c = Converter(src, dest, dict)
        c.run()
        os.chdir(cwd)
