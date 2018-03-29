import os
import unittest

from spinn_utilities.make_tools.file_convertor import FileConvertor

src = os.path.join("mock_src", "weird,file.c")
dest = os.path.join("modified_src", "weird,file.c")
csv = "weird,file.csv"


class TestConvertor(unittest.TestCase):

    @staticmethod
    def do_convert():
        FileConvertor.convert(src, dest, csv, 9000)

    def test_convert(self):
        if os.path.exists(csv):
            os.remove(csv)
        self.do_convert()
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
