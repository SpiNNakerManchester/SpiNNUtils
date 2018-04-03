import os
import spinn_utilities.make_tools.number_mapper as number_mapper

convert_dir = os.path.dirname(os.path.abspath(__file__))


def test_number_mapper_not_there():
    src = os.path.join(convert_dir, "mock_src")
    txt = os.path.join(src, "log_ranges.txt")
    if os.path.exists(txt):
        os.remove(txt)
    number_mapper.number_c_files(2000, 3000, "mock_src")
    txt = os.path.join(src, "log_ranges.txt")
    files_inc_txt = len(os.listdir(src))
    lines_inc_donot = sum(1 for line in open(txt))
    assert files_inc_txt == lines_inc_donot


def test_number_mapper_add():
    src = os.path.join(convert_dir, "mock_src")
    txt = os.path.join(src, "log_ranges.txt")
    number_mapper.number_c_files(2000, 3000, "mock_src")
    files_inc_txt = len(os.listdir(src))
    txt = os.path.join(src, "log_ranges.txt")
    lines_inc_donot = sum(1 for line in open(txt))
    assert files_inc_txt == lines_inc_donot
    temp = os.path.join(src, "temp.c")
    with open(temp, 'w') as temp_file:
        temp_file.write("blah blah blah")
    number_mapper.number_c_files(2000, 3000, "mock_src")
    lines_inc_donot = sum(1 for line in open(txt))
    assert (files_inc_txt + 1) == lines_inc_donot
    os.remove(temp)
