from spinn_utilities.executable_finder import ExecutableFinder
import unittest
import tempfile
import os

class TestExecFinder(unittest.TestCase):

    def test_create_and_config(self):
        a = tempfile.mkdtemp("a")
        b = tempfile.mkdtemp("b")
        ef = ExecutableFinder([str(a), str(b)])
        assert ef.binary_paths == "{} : {}".format(a, b)
        c = tempfile.mkdtemp("c")
        ef.add_path(str(c))
        assert ef.binary_paths == "{} : {} : {}".format(a, b, c)

    def test_find_in_no_places(self):
        ef = ExecutableFinder([])
        with self.assertRaises(Exception):
            ef.get_executable_path("abc.aplx")

    def test_find_in_one_place(self):
        tmp_dir = tempfile.mkdtemp("b")
        ef = ExecutableFinder([str(tmp_dir)])
        w_file = tmp_dir.join("abc.aplx")
        w = open(w_file)
        w.write("any old content")
        w.close()
        assert ef.get_executable_path("abc.aplx") == str(w)

    def test_find_in_two_places(self):
        a = tempfile.mkdtemp("a")
        b = tempfile.mkdtemp("b")
        ef = ExecutableFinder([str(a), str(b)])
        w_file = a.join("abc.aplx")
        w1 = open(w_file)
        w1.write("any old content")
        w1.close()
        w2_file = b.join("abc.aplx")
        w2 = open(w2_file)
        w2.write("any old content")
        w2.close()
        assert ef.get_executable_path("abc.aplx") == str(w1)
        os.remove(w_file)
        assert ef.get_executable_path("abc.aplx") == str(w2)
        w1 = open(w_file)
        w1.write("any old content")
        assert ef.get_executable_path("abc.aplx") == str(w1)
        os.remove(w2_file)
        assert ef.get_executable_path("abc.aplx") == str(w1)
        os.remove(w_file)
        with self.assertRaises(Exception):
            ef.get_executable_path("abc.aplx")

    def test_find_no_duplicates(self):
        a = tempfile.mkdtemp("a")
        b = tempfile.mkdtemp("b")
        ef = ExecutableFinder([str(a), str(b)])
        assert ef.binary_paths == "{} : {}".format(a, b)
        ef.add_path(str(a))
        ef.add_path(str(a))
        ef.add_path(str(b))
        ef.add_path(str(b))
        ef.add_path(str(a))
        ef.add_path(str(a))
        ef.add_path(str(b))
        ef.add_path(str(b))
        assert ef.binary_paths == "{} : {}".format(a, b)
