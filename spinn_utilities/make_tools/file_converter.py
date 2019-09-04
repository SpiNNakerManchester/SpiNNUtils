# Copyright (c) 2018 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import sys

TOKEN = chr(30)  # Record Separator

COMMA_SPLIITER = re.compile(r'(?!\B"[^"]*),(?![^"]*"\B)')
STRING_REGEXP = re.compile(r'"([^"]|\\"|(""))*"')
FORMAT_EXP = re.compile(r"(?:^|[^%])(%\d*(?:\.\d+)?[cdfiksuxRF])")
LOG_END_REGEX = re.compile(r'\)(\s)*;')
END_COMMENT_REGEX = re.compile(r"/*/")
LOG_START_REGEX = re.compile(
    r"log_((info)|(error)|(debug)|(warning))(\s)*\(")
DOUBLE_HEX = ", double_to_upper({0}), double_to_lower({0})"

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

MAX_LOG_PER_FILE = 100


class FileConverter(object):
    __slots__ = [
        # Full destination directory
        "_dest",
        # File to hold dictionary mappings
        "_dict",
        # original c log method found
        # variable created each time a log method found
        "_log",
        # Log methods found so far
        # variable created each time a log method found
        "_log_full",
        # Number of c lines the log method takes
        # variable created each time a log method found
        "_log_lines",
        # Any other stuff found before the log method but on same line
        # variable created each time a log method found
        "_log_start",
        # Id for next message
        "_message_id",
        # The previous state
        # variable created when a comment found
        "_previous_status",
        # Full source directory
        "_src",
        # Current status of state machine
        "_status",
        # Number of extra lines written to modified not yet recovered
        # Extra lines are caused by the header and possibly log comment
        # Extra lines are recovered by omitting blank lines
        "_too_many_lines"
    ]

    def __init__(self, src, dest, dict_file):
        """ Creates the file_convertor to convert one file

        :param src: Full source directory
        :type src: str
        :param dest: Full destination directory
        :type dest: str
        :param dict_file: File to hold dictionary mappings
        :type dict_file: str
        """
        self._src = os.path.abspath(src)
        self._dest = os.path.abspath(dest)
        self._dict = dict_file
        self._log = None
        self._log_full = None
        self._log_lines = None
        self._log_start = None
        self._message_id = None
        self._previous_status = None
        self._status = None
        self._too_many_lines = None

    def _run(self, range_start):
        """ Runs the file converter

        WARNING. This code is absolutely not thread safe.
        Interwoven calls even on different FileConverter objects is dangerous!
        It is highly likely that dict files become corrupted and the same
        message_id is used multiple times.


        :param range_start: id of last dictionary key used
        :type range_start: int
        :return: The last message id use which can in turn be passed into
        the next FileConverter
        """
        self._message_id = range_start
        if not os.path.exists(self._src):
            raise Exception("Unable to locate source {}".format(self._src))
        dest_dir = os.path.dirname(os.path.realpath(self._dest))
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        with open(self._src) as src_f:
            with open(self._dest, 'w') as dest_f:
                dest_f.write(
                    "// DO NOT EDIT! THIS FILE WAS GENERATED FROM {}\n\n"
                    .format(self.unique_src()))
                self._too_many_lines = 2
                self._status = NORMAL_CODE
                for line_num, text in enumerate(src_f):
                    if self._too_many_lines > 0:
                        # Try to recover the lines added by do not edit
                        check = text.strip()
                        if len(check) == 0 or check == "*":
                            self._too_many_lines -= 1
                            continue
                    previous_status = self._status
                    if not self._process_line(dest_f, line_num, text):
                        self._status = previous_status
                        self._process_chars(dest_f, line_num, text)
        # print (self._dest)
        return self._message_id

    def _process_line(self, dest_f, line_num, text):
        """ Process a single line

        :param dest_f: Open file like Object to write modified source to
        :param line_num: Line number in the source c file
        :param text: Text of that line including whitespace
        :return: True if and only if the whole line was processed
        """
        if self._status == COMMENT:
            return self._process_line_in_comment(dest_f, text)
        if "/*" in text:
            return self._process_line_comment_start(dest_f, line_num, text)

        if self._status == IN_LOG:
            return self._process_line_in_log(dest_f, line_num, text)

        if self._status == IN_LOG_CLOSE_BRACKET:
            return self._process_line_in_log_close_bracket(
                dest_f, line_num, text)

        assert self._status == NORMAL_CODE
        return self._process_line_normal_code(dest_f, line_num, text)

    def _process_line_in_comment(self, dest_f, text):
        """ Process a single line when in a multi line comment /*  .. */

        :param dest_f: Open file like Object to write modified source to
        :param text: Text of that line including whitespace
        :return: True if and only if the whole line was processed
        """
        if "*/" in text:
            stripped = text.strip()
            match = END_COMMENT_REGEX.search(stripped)
            if match.end(0) == len(stripped):
                # OK Comment until end of line
                dest_f.write(text)
                self._status = NORMAL_CODE
                return True
            return False  # Stuff after comment so check by character
        # Whole line in comment without end
        dest_f.write(text)
        return True

    def _process_line_comment_start(self, dest_f, line_num, text):
        """ Processes a line known assumed to contain a /* but not know where

        There is also the assumption that the start status is not COMMENT

        :param dest_f: Open file like Object to write modified source to
        :param line_num: Line number in the source c file
        :param text: Text of that line including whitespace
        :return: True if and only if the whole line was processed
        """
        stripped = text.strip()
        if stripped.startswith("/*"):
            self._previous_status = self._status
            self._status = COMMENT
            # Comment start so now check for comment end
            return self._process_line(dest_f, line_num, text)
        # Stuff before comment so check by char
        return False  # More than one possible end so check by char

    def _process_line_in_log(self, dest_f, line_num, text):
        """ Process a line when the status is a log call has been started

        :param dest_f: Open file like Object to write modified source to
        :param line_num: Line number in the source c file
        :param text: Text of that line including whitespace
        :return: True if and only if the whole line was processed
        """
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
        self._write_log_method(dest_f, line_num)
        self._status = NORMAL_CODE
        return True

    def _process_line_in_log_close_bracket(self, dest_f, line_num, text):
        """ Process where the last log line has the ) but not the ;

        :param dest_f: Open file like Object to write modified source to
        :param line_num: Line number in the source c file
        :param text: Text of that line including whitespace
        :return: True if and only if the whole line was processed
        """
        stripped = text.strip()
        if len(stripped) == 0:
            self._log_lines += 1
            return True
        if stripped[0] == ";":
            if stripped == ";":
                self._log_full += (";")
                self._log_lines += 1
                self._write_log_method(dest_f, line_num)
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
            return self._process_line_in_log(dest_f, line_num, text)

    def _process_line_normal_code(self, dest_f, line_num, text):
        """ Process a line where the status is normal code

        :param dest_f: Open file like Object to write modified source to
        :param line_num: Line number in the source c file
        :param text: Text of that line including whitespace
        :return: True if and only if the whole line was processed
        """
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

        # remove white spaces and save log command
        self._log_start = text.index(match.group(0))
        self._log = "".join(match.group(0).split())
        start_len = self._log_start + len(self._log)

        self._status = IN_LOG
        self._log_full = ""  # text saved in process_line_in_log
        self._log_lines = 0
        # Now check for the end of log command
        return self._process_line_in_log(dest_f, line_num, text[start_len:])

    def quote_part(self, text):
        return (text.count('"') - text.count('\\"')) % 2 > 0

    def bracket_count(self, text):
        return (text.count('(') - text.count(')'))

    def split_by_comma_plus(self, main, line_num):
        try:
            parts = main.split(",")
            for i, part in enumerate(parts):
                check = part.strip()
                if check[0] == '"':
                    # Dealing with a String
                    if check[-1] == '"':
                        if check[-2] != '\\':
                            # Part is a full sting fine
                            continue
                    # Save start of String and get next part
                    new_part = parts.pop(i)
                    next_part = parts.pop(i)
                    new_check = next_part.strip()
                    while new_check[-1] != '"' or new_check[-2] == '\\':
                        # Still not end of String so add and get next
                        new_part += "," + next_part
                        next_part = parts.pop(i)
                        new_check = next_part.strip()
                    # Add the end and put back new in the list
                    new_part += "," + next_part
                    parts.insert(i, new_part)
                else:
                    # Not a String so look for function
                    count = self.bracket_count(part)
                    if (count > 0):
                        # More opening and closing brackets so in function
                        new_part = parts.pop(i)
                        # Keep combining parts until you find the last closing
                        while count > 0:
                            next_part = parts.pop(i)
                            count += self.bracket_count(next_part)
                            new_part += "," + next_part
                        # Put the new part back into the list
                        parts.insert(i, new_part)
            if parts[0][0] == '"' and parts[0][-1] == '"':
                parts[0] = parts[0][1:-1]
            return parts

        except Exception:
            raise Exception("Unexpected line {} at {} in {}".format(
                self._log_full, line_num, self._src))

    def _short_log(self, line_num):
        """ shortens the log string message and adds the id

        Assumes that self._message_id has already been updated

        :param original: Source log messages
        :return: new log message and the id
        """
        try:
            match = LOG_END_REGEX.search(self._log_full)
            main = self._log_full[:-len(match.group(0))]
        except Exception:
            raise Exception("Unexpected line {} at {} in {}".format(
                self._log_full, line_num, self._src))
        parts = self.split_by_comma_plus(main, line_num)
        original = parts[0]
        count = original.count("%") - original.count("%%")*2
        if count == 0:
            return original, '"%u", {});'.format(self._message_id)
        else:
            front = '"%u'
            back = ""
            matches = FORMAT_EXP.findall(original)
            if len(matches) != count:
                raise Exception(
                    "Unexpected formatString in {}".format(original))
            if len(parts) < count + 1:
                raise Exception("Too few parameters in line {} at {} in "
                                "{}".format(self._log_full, line_num,
                                            self._src))
            if len(parts) > count + 1:
                raise Exception("Too many parameters in line {} at {} in "
                                "{}".format(self._log_full, line_num,
                                            self._src))
            for i, match in enumerate(matches):
                front += TOKEN
                if match.endswith("f"):
                    front += "%x"
                elif match.endswith("F"):
                    front += "%x" + TOKEN + "%x"
                else:
                    front += match
                if match.endswith("f"):
                    back += ", float_to_int({})".format(parts[i + 1])
                elif match.endswith("F"):
                    back += DOUBLE_HEX.format(parts[i + 1])
                else:
                    back += ", {}".format(parts[i+1])
            front += '", {}'.format(self._message_id)
            back += ");"
        return original, front + back

    def _write_log_method(self, dest_f, line_num, tail=""):
        """ Writes the log message and the dict value

        Writes the log call to the destination
        - New log method used
        - Shortened log message (with just an id) used
        - Parameters kept as is
        - Old log message with full text added as comment

        Adds the data to the dict file including
        - key/id
        - log level
        - file name
        - line number
        - original message

        :param dest_f: Open file like Object to write modified source to
        :param line_num: Line number in the source c file
        :param text: Text of that line including whitespace
        """
        self._message_id += 1
        self._log_full = self._log_full.replace('""', '')
        original, short_log = self._short_log(line_num)

        dest_f.write(" " * self._log_start)
        dest_f.write(MINIS[self._log])
        dest_f.write(short_log)
        if self._log_lines == 0:
            # Writing an extra newline here so need to recover that ASAP
            self._too_many_lines += 1
        end = tail + "\n"
        if self._log_lines <= 1:
            dest_f.write("  /* ")
            dest_f.write(self._log)
            dest_f.write(self._log_full)
            dest_f.write("*/")
            dest_f.write(end)
        else:
            dest_f.write(tail)
            dest_f.write(end)
            dest_f.write(" " * self._log_start)
            dest_f.write("/* ")
            dest_f.write(self._log)
            dest_f.write(self._log_full)
            dest_f.write("*/")
            dest_f.write(end * (self._log_lines - 1))
        with open(self._dict, 'a') as mess_f:
            # Remove commas from filenames for csv format
            # Remove start and end quotes from original
            mess_f.write("{},{} ({}: {}): ,{}\n".format(
                self._message_id, LEVELS[self._log],
                os.path.basename(self._src).replace(",", ";"),
                line_num + 1,
                original))

    def _process_chars(self, dest_f, line_num, text):
        """ Deals with complex lines that can not be handled in one go

        :param dest_f: Open file like Object to write modified source to
        :param line_num: Line number in the source c file
        :param text: Text of that line including whitespace
        """
        pos = 0
        write_flag = 0
        while text[pos] != "\n":
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
                        if self._log_full[-1] == ")":
                            self._status = IN_LOG_CLOSE_BRACKET
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
                            format(self._src, line_num))
                    elif text[str_pos] == "\\":
                        if text[str_pos+1] == "\n":
                            raise Exception(
                                "Unclosed string literal in {} at line: {}".
                                format(self._src, line_num))

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
                            # check for a \ after the log
                            if text[pos:].strip() == "\\":
                                self._write_log_method(dest_f, line_num, "\\")
                                return
                            else:
                                self._write_log_method(dest_f, line_num)
                        else:
                            self._log_lines += 1
                            self._write_log_method(dest_f, line_num)
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
                    self._write_log_method(dest_f, line_num)
                    pos = text.index(";") + 1
                    write_flag = pos
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
                    # skip to end of log instruction
                    pos = pos + len(match.group(0))
                    write_flag = pos
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

    def unique_src(self):
        """ Returns the part of the source path which is different

        For example assuming a source of
        /spinnaker/sPyNNaker/neural_modelling/src/common/in_spikes.h
        /spinnaker/sPyNNaker/neural_modelling/modified_src/common/in_spikes.h
        returns src/common/in_spikes.h

        :return: A pointer to the source relative to the destination
        """
        pos = 0
        last_sep = 0
        while pos < len(self._src) and pos < len(self._dest) \
                and self._src[pos] == self._dest[pos]:
            if self._src[pos] == os.path.sep:
                last_sep = pos + 1
            pos += 1
        return self._src[last_sep:]

    @staticmethod
    def convert(src, dest, dict_file, range_start):
        """ Static method to create Object and do the conversion

        :param src: Full source directory
        :type src: str
        :param dest: Full destination directory
        :type dest: str
        :param dict_file: File to hold dictionary mappings
        :type dict_file: str
        :param range_start:
        :param range_start: id of last dictionary key used
        :type range_start: int
        :return: The last message id use which can in turn be passed into
        """
        converter = FileConverter(src, dest, dict_file)
        return converter._run(range_start)  # pylint: disable=protected-access


if __name__ == '__main__':
    _src = sys.argv[1]
    _dest = sys.argv[2]
    _dict_file = sys.argv[3]
    _range_start = int(sys.argv[4])
    FileConverter.convert(_src, _dest, _dict_file, _range_start)
