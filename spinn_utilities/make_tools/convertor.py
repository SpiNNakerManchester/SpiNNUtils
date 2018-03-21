from datetime import datetime
import os
import math
import re
import shutil
import sys

STRING_REGEXP = re.compile('"([^"]|\\"|(""))*"')
FORMATEXP = re.compile("%\d*(?:\.\d+)?[diksuxR]")


class Convertor(object):
    # __slots__ = [
    #    "_dest", "_dest_basename", "_src", "_src_basename"]

    REGEXP = re.compile("%(?:\d+\$)?[dfsu]")

    def __init__(self, src, dest, start):
        self._src = src
        if not os.path.exists(self._src):
            raise Exception("Unable to locate source directory {}".format(src))
        self._dest = dest
        src_root, src_basename = os.path.split(
            os.path.normpath(self._src))
        dest_root, dest_basename = os.path.split(
            os.path.normpath(self._dest))
        if src_root != dest_root:
            # They must be siblings due to text manipulation in makefiles
            raise Exception("src and destination must be siblings")
        self._src_basename = "/" + src_basename + "/"
        self._dest_basename = "/" + dest_basename + "/"
        self._mkdir(self._dest)
        convertor_path = os.path.dirname(os.path.abspath(__file__))
        self._messages = os.path.join(
            convertor_path, "messages{}.csv".format(start))
        with open(self._messages, 'w') as mess_f:
            mess_f.write("id, level, line, file, original\n"
                         "This list was generated {}\n\n".format(
                datetime.today()))
        self._message_id = start

    def run(self):
        for dirName, subdirList, fileList in os.walk(self._src):
            self._mkdir(dirName)
            for fileName in fileList:
                _, extension = os.path.splitext(fileName)
                path = os.path.join(dirName, fileName)
                if fileName in ["Makefile"]:
                    self.convert_make(path)
                elif fileName in [".gitignore", "Makefile.common",
                                  "Makefile.neural_build", "Makefile.paths"]:
                    pass
                elif extension in [".mk"]:
                    self.convert_make(path)
                elif extension in [".c", ".cpp", ".h"]:
                    self.convert_c(path, fileName)
                elif extension in [".elf", ".o", ".nm", ".txt"]:
                    self.copy_if_newer(path)
                else:
                    print ("Unexpected file {}".format(path))
                    self.copy_if_newer(path)

    def convert_make(self, src_path):
        destination = self._check_destination(src_path)
        if destination is None:
            return  # newer so no need to copy
        with open(src_path) as src_f:
            with open(destination, 'w') as dest_f:
                dest_f.write(
                    "# DO NOT EDIT! THIS FILE WAS GENERATED FROM {}\n\n"
                    .format(src_path))
                for line in src_f:
                    line_dest = line.replace(
                        self._src_basename, self._dest_basename)
                    dest_f.write(line_dest)

    def _start_log(self, text):
        self._log_type = None
        # checking stripped ignores comments and text elsewhere
        stripped = text.strip()
        if stripped.startswith("log_info"):
            self._log_original = "log_info"
            self._log_mini = "log_mini_info"
        elif stripped.startswith("log_error"):
            self._log_original = "log_error"
            self._log_mini = "log_mini_error"
        elif stripped.startswith("log_debug"):
            self._log_original = "log_debug"
            self._log_mini = "log_mini_debug"
        elif stripped.startswith("log_warning"):
            self._log_original = "log_warning"
            self._log_mini = "log_mini_warning"
        else:
            return False

        self._log_start = text.index(self._log_original)
        # Empty full and lines as end_log called on first line too
        self._log_full = ""
        self._log_lines = 0
        return True

    def shorten(self, text):
        count = text.count("%")
        if count == 0:
            return '"%u", {}'.format(self._message_id)
        else:
            result = '"%u'
            matches = FORMATEXP.findall(text)
            if len(matches) != count:
                raise Exception("Unexpected formatString in {}".format(text))
            for match in matches:
                result += " "
                result += match
            return result + '", {}'.format(self._message_id)

    def _end_log(self, text, line, fileName, dest_f):
        self._log_full += text.strip()
        self._log_lines += 1
        # may need a more complex test but lets start easy
        if ");" not in self._log_full:
            return True  # Still inside a log
        else:
            self._log_full = self._log_full.replace('""','')
            self._message_id += 1
            original = STRING_REGEXP.search(self._log_full).group(0)
            replacement = self.shorten(original)
            dest_f.write(" " * self._log_start)
            dest_f.write(
                self._log_full.replace(self._log_original, self._log_mini).
                    replace(original, replacement))
            if (self._log_lines == 1):
                dest_f.write("  // ")
                dest_f.write(original)
                dest_f.write("\n")
            else:
                dest_f.write("\n")
                dest_f.write(" " * self._log_start)
                dest_f.write("// ")
                dest_f.write(original)
                dest_f.write("\n" * (self._log_lines - 1))
            with open(self._messages, 'a') as mess_f:
                mess_f.write("{}, {}, {}, {}, {}\n".format(
                    self._message_id, self._log_original, line + 1, fileName,
                    original))
            return False  # No longer in log

    def convert_c(self, src_path, fileName):
        destination = self._check_destination(src_path)
        if destination is None:
            return  # newer so no need to copy
        with open(src_path) as src_f:
            with open(destination, 'w') as dest_f:
                dest_f.write(
                    "// DO NOT EDIT! THIS FILE WAS GENERATED FROM {}\n\n"
                    .format(src_path))
                too_many_lines = 2
                in_log = False
                for line, text in enumerate(src_f):
                    if too_many_lines:
                        # Try to recover the lines added by do not edit
                        check = text.strip()
                        if len(check) == 0 or check == "*":
                            too_many_lines -= 1
                            continue
                    if not in_log:
                        in_log = self._start_log(text)
                    if in_log:
                        in_log = self._end_log(text, line, fileName, dest_f)
                    else:
                        dest_f.write(text)

        self.copy_if_newer(src_path)

    def copy_if_newer(self, src_path):
        destination = self._check_destination(src_path)
        if destination is None:
            return  # newer so no need to copy
        shutil.copy2(src_path, destination)

    def _check_destination(self, path):
        destination = path.replace(self._src_basename, self._dest_basename)
        if not os.path.exists(destination):
            return destination
        # need to floor the time as some copies ignore the partial second
        src_time = math.floor(os.path.getmtime(path))
        dest_time = math.floor(os.path.getmtime(destination))
        if src_time > dest_time:
            return destination
        else:
            # print ("ignoring {}".format(destination))
            return None

    def _mkdir(self, path):
        destination = path.replace(self._src_basename, self._dest_basename)
        if not os.path.exists(destination):
            os.mkdir(destination, 0755)
        if not os.path.exists(destination):
            raise Exception("mkdir failed {}".format(destination))


def convert(src, modified, messages):
    convertor = Convertor(src, modified, messages)
    convertor.run()


if __name__ == '__main__':
    print (sys.argv)
    src = os.path.abspath(sys.argv[1])
    print ("src: {}".format(src))
    dest = os.path.abspath(sys.argv[2])
    print ("dest: {}".format(dest))
    start = int(sys.argv[3])
    print ("start: {}".format(start))
    convert(src, dest, start)
