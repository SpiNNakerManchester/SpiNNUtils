import os
import unittest

from unittests.make_tools.test_convert import TestConvertor
from spinn_utilities.make_tools.replacer import Replacer


class TestReplacer(unittest.TestCase):

    def setUp(self):
        global replacer
        convert_dir = os.path.dirname(os.path.abspath(__file__))
        replacer = Replacer(convert_dir)

    def test_replace(self):
        assert "[DEBUG] (neuron.c: 140): -------------------------------------\n" == \
               replacer.replace("9001")
