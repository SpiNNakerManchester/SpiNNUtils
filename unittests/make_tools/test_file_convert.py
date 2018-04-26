import os
import unittest

from spinn_utilities.make_tools.file_convertor import FileConvertor

ranged_file = "local_ranges.txt"


class TestConvertor(unittest.TestCase):

    @staticmethod
    def do_convert(file_name):
        src = os.path.join("mock_src", file_name)
        dest = os.path.join("modified_src", file_name)
        FileConvertor.convert(src, dest, ranged_file, 2000)

    def test_convert(self):
        file_name = "weird,file.c"
        self.do_convert(file_name)
        src = os.path.join("mock_src", file_name)
        dest = os.path.join("modified_src", file_name)
        csv = dest + ".csv"
        src_lines = sum(1 for line in open(src))
        modified_lines = sum(1 for line in open(dest))
        self.assertEquals(src_lines, modified_lines)
        with open(csv, 'r') as csvfile:
            data = csvfile.read()
        assert("this is ok" in data)
        assert("this is ok" in data)
        assert("this is fine on two lines" in data)
        assert("before comment after comment" in data)
        assert("One line commted" in data)
        assert("this is for alan); so there!" in data)
        assert("Test %u for alan); so there!" in data)
        assert("\\t back off = %u, time between spikes %u" in data)
        assert("the neuron %d has been determined to not spike" in data)
        assert("Inside a loop" in data)
        assert("then a space" in data)
        assert("then a newline simple" in data)
        assert("then a newline plus" in data)
        assert("first" in data)
        assert("second" in data)
        assert("then a backslash comment on a middle line" in data)
        assert("then a standard comment on a middle line" in data)
        assert("comment before" in data)

    def test_multiple(self):
        if os.path.exists(ranged_file):
            os.remove(ranged_file)
        self.do_convert("weird,file.c")
        self.do_convert("common-typedefs.h")
        range_lines = sum(1 for line in open(ranged_file))
        self.assertEquals (3, range_lines)
