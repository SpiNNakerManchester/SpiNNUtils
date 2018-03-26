import os
import unittest

from spinn_utilities.make_tools.convertor import Convertor

convert_dir = os.path.dirname(os.path.abspath(__file__))


class TestConvertor(unittest.TestCase):

    @staticmethod
    def do_convert():
        src = os.path.join(convert_dir, "mock_src")
        dest = os.path.join(convert_dir, "modified_src")

        convertor = Convertor(src, dest, 9000, convert_dir)
        convertor.run()

    def test_convert(self):
        messages = os.path.join(convert_dir, "messages9000.csv")
        if os.path.exists(messages):
            os.remove(messages)
        self.do_convert()
        weird_src = os.path.join(convert_dir, "mock_src", "weird,file.c")
        weird_modified = os.path.join(
            convert_dir, "modified_src", "weird,file.c")
        src_lines = sum(1 for line in open(weird_src))
        modified_lines = sum(1 for line in open(weird_modified))
        self.assertEquals(src_lines, modified_lines)
        with open(messages, 'r') as myfile:
            data = myfile.read()
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
