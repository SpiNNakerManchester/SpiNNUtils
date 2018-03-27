from datetime import datetime
import os
import math
import re
import shutil
import sys

STRING_REGEXP = re.compile('"([^"]|\\"|(""))*"')
FORMATEXP = re.compile("%\d*(?:\.\d+)?[diksuxR]")
LOG_END_REGEX = re.compile('\)(\s)*;')
END_COMMENT_REGEX = re.compile("/*/")
LOG_START_REGEX = re.compile(
    "log_((info)|(error)|(debug)|(warning))(\s)*\(")

# Status values
NORMAL_CODE = 0
COMMENT = NORMAL_CODE + 1
IN_LOG = COMMENT + 1
IN_LOG_CLOSE_BRACKET = IN_LOG + 1

MINIS = {"log_info(": "log_mini_info(",
         "log_error(": "log_mini_error(",
         "log_debug(": "log_mini_debug(",
         "log_warning(": "log_mini_warning("}

LEVELS = {"log_info(": "[INFO]",
          "log_error(": "[ERROR]",
          "log_debug(": "[DEBUG]",
          "log_warning(": "[WARNING]"}

# COMMENT_EXPRESSION = re.compile('/\*.*\*/')


class Convertor(object):
    # __slots__ = [
    #    "_dest", "_dest_basename", "_src", "_src_basename"]

    REGEXP = re.compile("%(?:\d+\$)?[dfsu]")

    def __init__(self, src, dest, start, convertor_dir=None):
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
        self._src_basename = src_basename
        self._dest_basename = dest_basename
        self._mkdir(self._dest)
        if convertor_dir is None:
            convertor_dir = os.path.dirname(os.path.abspath(__file__))

        self._messages = os.path.join(
            convertor_dir, "messages{}.csv".format(start))
        with open(self._messages, 'w') as mess_f:
            mess_f.write("Id,Preface,Original\n"
                         ",,This list was generated {}\n\n".format(
                datetime.today()))
        self._message_id = start

    def run(self):
        for dirName, subdirList, fileList in os.walk(self._src):
            self._mkdir(dirName)
            for file_name in fileList:
                _, extension = os.path.splitext(file_name)
                path = os.path.join(dirName, file_name)
                if file_name in ["Makefile"]:
                    self.convert_make(path)
                elif extension in [".mk"]:
                    self.convert_make(path)
                elif extension in [".c", ".cpp", ".h"]:
                    self.convert_c(path, file_name)
                elif extension in [".elf", ".o", ".nm", ".txt"]:
                    self.copy_if_newer(path)
                elif file_name in [".gitignore"]:
                    pass
                elif file_name in ["Makefile.common",
                                  "Makefile.neural_build",
                                  "Makefile.paths",
                                  "Makefile.SpiNNFrontEndCommon"]:
                    self.copy_if_newer(path)
                else:
                    print ("Unexpected file {}".format(path))
                    self.copy_if_newer(path)

    def convert_make(self, src_path):
        destination = self._newer_destination(src_path)
        if destination is None:
            return  # newer so no need to copy
        with open(src_path) as src_f:
            with open(destination, 'w') as dest_f:
                dest_f.write(
                    "# DO NOT EDIT! THIS FILE WAS GENERATED FROM {}\n\n"
                    .format(src_path))
                for line in src_f:
                    # Here we need the linux seperator even on windows
                    line_dest = line.replace(
                        "/" + self._src_basename + "/",
                        "/" + self._dest_basename + "/")
                    dest_f.write(line_dest)

    def convert_c(self, src_path, file_name):
        destination = self._any_destination(src_path)
        with open(src_path) as src_f:
            with open(destination, 'w') as dest_f:
                dest_f.write(
                    "// DO NOT EDIT! THIS FILE WAS GENERATED FROM {}\n\n"
                    .format(src_path))
                self._too_many_lines = 2
                in_log = False
                self._status = NORMAL_CODE
                for line_num, text in enumerate(src_f):
                    if self._too_many_lines > 0:
                        # Try to recover the lines added by do not edit
                        check = text.strip()
                        if len(check) == 0 or check == "*":
                            self._too_many_lines -= 1
                            continue
                    if not self._process_line(
                            text, dest_f, file_name, line_num):
                        self._comment_start = 0
                        self._process_chars(text, dest_f, file_name, line_num)

    def _process_line(self, text, dest_f, file_name, line_num):
        if self._status == COMMENT:
            return self._process_line_in_comment(text, dest_f)

        if "/*" in text:
            return self._process_line_comment_start(
                text, dest_f, file_name, line_num)

        if self._status == IN_LOG:
            return self._process_line_in_log(text, dest_f, file_name, line_num)

        if self._status == IN_LOG_CLOSE_BRACKET:
            return self._process_line_in_log_close_bracket(
                text, dest_f, file_name, line_num)

        assert self._status == NORMAL_CODE
        return self._process_line_normal_code(text, dest_f, file_name, line_num)

    def _process_line_in_comment(self, text, dest_f):
        if "*/" in text:
            stripped = text.strip()
            match = END_COMMENT_REGEX.search(stripped)
            if match.end(0) == len(stripped):
                # Ok Comment until end of line
                dest_f.write(text)
                self._status = NORMAL_CODE
                return True
            return False  # Stuff after comment so check by character
        # Whole line in comment without end
        dest_f.write(text)
        return True

    def _process_line_comment_start(self, text, dest_f, file_name, line_num):
        """ Processes a known assumed to contain a /* but not know where

        There is aslo the assumption that the start status is not COMMENT

        :param text:
        :param dest_f:
        :param file_name:
        :param line_num:
        :return:
        """
        stripped = text.strip()
        if stripped.startswith("/*"):
            self._previous_status = self._status
            self._status = COMMENT
            # Comment start so now check for comment end
            return self._process_line(text, dest_f, file_name, line_num)
        # Stuff before comment so check by char
        return False  # More than one possible end so check by char

    def _process_line_in_log(self, text, dest_f, file_name, line_num):
        stripped = text.strip()
        if stripped.startswith("//"):
            # Just a comment line so write and move on
            dest_f.write(text)
            return True

        match = LOG_END_REGEX.search(stripped)
        if not match:
            if stripped[-1:] == ")":
                # possible start of end
                self._status = IN_LOG_CLOSE_BRACKET
            self._log_full += stripped
            self._log_lines += 1
            return True
        if match.end(0) < len(stripped):
            # Stuff after the log_end so check by char
            return False

        self._log_lines += 1
        self._log_full += stripped
        self._write_log_method(dest_f, file_name, line_num)
        self._status = NORMAL_CODE
        return True

    def _process_line_in_log_close_bracket(self, text, dest_f, file_name, line_num):
        stripped = text.strip()
        if stripped[0] == ";":
            if stripped == ";":
                self._log_full += (";")
                self._log_lines += 1
                self._write_log_method(dest_f, file_name, line_num)
                self._status = NORMAL_CODE
                return True
            else:
                return False

        elif stripped.startswith("//"):
            # Just a comment line so write and move on
            dest_f.write(text)
            return True

        else:
            # so not a closing bracket so set status back
            self._status = IN_LOG
            return self._process_line_in_log(text, dest_f, file_name, line_num)

    def _process_line_normal_code(self, text, dest_f, file_name, line_num):
        # Fast check
        if "log_" not in text:
            # No log start found
            dest_f.write(text)
            return True

        # Full slower check
        stripped = text.strip()
        match = LOG_START_REGEX.search(stripped)
        if not match:
            # No log start found after all
            dest_f.write(text)
            return True

        if match.start() > 0:
            if stripped.startswith("//"):
                # Just a comment line so write and move on
                dest_f.write(text)
                return True
            # Stuff before the log_start so check by character
            return False

        if LOG_START_REGEX.search(stripped, 1):
            # Second start found so check by character
            return False

        # remove whitespaces and save log command
        self._log_start = text.index(match.group(0))
        self._log = "".join(match.group(0).split())
        self._status = IN_LOG
        self._log_full = ""  # text saved in process_line_in_log
        self._log_lines = 0
        # Now check for the end of log command
        return self._process_line_in_log(text, dest_f, file_name, line_num)

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

    def _write_log_method(self, dest_f, file_name, line_num):
        self._message_id += 1
        self._log_full = self._log_full.replace('""', '')
        original = STRING_REGEXP.search(self._log_full).group(0)
        replacement = self.shorten(original)
        self._log_full = self._log_full.replace(self._log, MINIS[self._log])\
            .replace(original, replacement)
        dest_f.write(" " * self._log_start)
        dest_f.write(self._log_full)
        if self._log_lines == 0:
            # Writing an extra newline here so need to recover that ASAP
            self._too_many_lines += 1
        if (self._log_lines <= 1):
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
            # Remove commas from filenames for csv format
            # Remove start and end quotes from original
            mess_f.write("{},{} ({}: {}): ,{}\n".format(
                self._message_id, LEVELS[self._log],
                file_name.replace(",", ";"), line_num + 1, original[1:-1]))

    def _process_chars(self, text, dest_f, file_name, line_num):
        pos = 0
        write_flag = 0
        while text[pos] != "\n":
            a = text[pos]
            if self._status == COMMENT:
                if text[pos] == "*" and text[pos+1] == "/":
                    dest_f.write(text[write_flag:pos + 2])
                    pos = pos + 2
                    write_flag = pos
                    self._status = self._previous_status
                else:
                    pos = pos + 1

            elif text[pos] == "/":
                if text[pos+1] == "*":
                    if self._status == IN_LOG:
                        self._log_full += text[write_flag:pos].strip()
                        # NO change to self._log_lines as newline not removed
                    else:
                        dest_f.write(text[write_flag:pos])
                    write_flag = pos
                    pos = pos + 2  # leave the /* as not written
                    self._previous_status = self._status
                    self._status = COMMENT
                elif text[pos+1] == "/":
                    if self._status == IN_LOG:
                        self._log_full += text[write_flag:pos].strip()
                        # NO change to self._log_lines as newline not removed
                        dest_f.write(text[pos:])
                    else:
                        dest_f.write(text[write_flag:])
                    return  # Finished line
                else:
                    pos += 1

            elif text[pos] == '"':
                str_pos = pos + 1
                while text[str_pos] != '"':
                    if text[str_pos] == "\n":
                        raise Exception(
                            "Unclosed string literal in {} at line: {}".
                                format(file_name, line_num))
                    elif text[str_pos] == "\\":
                        if text[str_pos+1] == "\n":
                            raise Exception(
                                "Unclosed string literal in {} at line: {}".
                                    format(file_name, line_num))

                        else:
                            str_pos += 2  # ignore next char which may be a "
                    else:
                        str_pos += 1
                pos = str_pos + 1
                continue

            elif self._status == IN_LOG:
                if text[pos] == ")":
                    match = LOG_END_REGEX.match(text[pos:])
                    if match:
                        # include the end
                        pos = pos + len(match.group(0))
                        self._log_full += text[write_flag:pos].strip()
                        self._status = NORMAL_CODE
                        if text[pos:].strip():  # Stuff left
                            write_flag = pos
                            # self._log_lines not changed as no newline
                            self._write_log_method(dest_f, file_name, line_num)
                        else:
                            self._log_lines += 1
                            self._write_log_method(dest_f, file_name, line_num)
                            return  # Finished line
                    else:
                        # not the require ); so continue
                        pos += 1
                else:
                    pos += 1

            elif self._status == IN_LOG_CLOSE_BRACKET:
                stripped = text.strip()
                if stripped[0] == ";":
                    self._log_full += (";")
                    self._write_log_method(dest_f, file_name, line_num)
                    pos = text.index(";") + 1
                    write_flag == pos
                    self._status = NORMAL_CODE
                else:
                    # Save the ) as not part of the end
                    self._status = IN_LOG

            elif text[pos] == "l":
                match = LOG_START_REGEX.match(text[pos:])
                if match:
                    self._log_start = text.index(match.group(0))
                    self._log = "".join(match.group(0).split())
                    self._status = IN_LOG
                    self._log_full = ""  # text saved after while
                    self._log_lines = 0
                    dest_f.write(text[write_flag:pos])
                    # written up to not including log_start
                    write_flag = pos
                    # skip to end of log start
                    pos = pos + len(match.group(0))
                else:
                    # Not a log start after all so treat as normal test
                    pos += 1

            else:
                pos += 1

        # after while text[pos] != "\n"
        if self._status == IN_LOG:
            self._log_full += text[write_flag:].strip()
            self._log_lines += 1
        else:
            dest_f.write(text[write_flag:])

    def copy_if_newer(self, src_path):
        destination = self._newer_destination(src_path)
        if destination is None:
            return  # newer so no need to copy
        shutil.copy2(src_path, destination)

    def _any_destination(self, path):
        # Here we need the local seperator
        destination = path.replace(
            os.path.sep + self._src_basename + os.path.sep,
            os.path.sep + self._dest_basename + os.path.sep)
        return destination

    def _newer_destination(self, path):
        destination = self._any_destination(path)
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
        destination = self._any_destination(path)
        if not os.path.exists(destination):
            os.mkdir(destination, 0755)
        if not os.path.exists(destination):
            raise Exception("mkdir failed {}".format(destination))

def convert(src, modified, messages):
    convertor = Convertor(src, modified, messages)
    convertor.run()


if __name__ == '__main__':
    src = os.path.abspath(sys.argv[1])
    dest = os.path.abspath(sys.argv[2])
    start = int(sys.argv[3])
    convert(src, dest, start)
