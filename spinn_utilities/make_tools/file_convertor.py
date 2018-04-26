import os
import re
import sys

TOKEN = chr(30)  # Record Sperator

STRING_REGEXP = re.compile('"([^"]|\\"|(""))*"')
FORMATEXP = re.compile("%\d*(?:\.\d+)?[cdiksuxR]")
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

MAX_LOG_PER_FILE = 100


class FileConvertor(object):
    # __slots__ = [
    #    "_dest", "_dest_basename", "_src", "_src_basename"]

    # REGEXP = re.compile("%(?:\d+\$)?[dfsu]")

    def __init__(self, src, dest, dict, range_start):
        self._src = os.path.abspath(src)
        self._dest = os.path.abspath(dest)
        self._message_id = range_start
        self._dict = dict

    def run(self):
        if not os.path.exists(self._src):
            raise Exception("Unable to locate source {}".format(src))
        dest_dir = os.path.dirname(os.path.realpath(self._dest))
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir, 0755)
        self.convert_c()
        return self._message_id

    def convert_c(self):
        with open(self._src) as src_f:
            with open(self._dest, 'w') as dest_f:
                dest_f.write(
                    "// DO NOT EDIT! THIS FILE WAS GENERATED FROM {}\n\n"
                    .format(self.unique_src()))
                self._too_many_lines = 2
                self._status = NORMAL_CODE
                for self._line_num, self._text in enumerate(src_f):
                    if self._too_many_lines > 0:
                        # Try to recover the lines added by do not edit
                        check = self._text.strip()
                        if len(check) == 0 or check == "*":
                            self._too_many_lines -= 1
                            continue
                    if not self._process_line(dest_f):
                        self._comment_start = 0
                        self._process_chars(dest_f)
        # print (self._dest)
        return self._message_id

    def _process_line(self, dest_f):
        if self._status == COMMENT:
            return self._process_line_in_comment(dest_f)
        if "/*" in self._text:
            return self._process_line_comment_start(dest_f)

        if self._status == IN_LOG:
            return self._process_line_in_log(dest_f)

        if self._status == IN_LOG_CLOSE_BRACKET:
            return self._process_line_in_log_close_bracket(dest_f)

        assert self._status == NORMAL_CODE
        return self._process_line_normal_code(dest_f)

    def _check_token(self):
        """ Crude check for the TOKEN in the whole c code.

        Ignores TOKENS in // comments
        but so far falls over on a TOKEN in a /* */ style comment.
        If needed could be altered to handle those as well.

        Also note that is is just a safety check and not stricktly required.

        A TOKEN in the c code only matters if it is in a String
        or other value that gets passed into a log call as a parameter.
        The TOKEN in the raw String message that gets replaced is ok.
        Even then all that happens is that this particular message is not
        Translated back into a proper String
        """
        if TOKEN not in self._text:
            return
        location = self._text.find(TOKEN)
        if "//" in self._text:
            if self._text.find("//") < location:
                return
        raise Exception("Unexpected line {} at {} in {}".format(
            self._text, self._line_num, self._src))

    def _process_line_in_comment(self, dest_f):
        if "*/" in self._text:
            stripped = self._text.strip()
            match = END_COMMENT_REGEX.search(stripped)
            if match.end(0) == len(stripped):
                # Ok Comment until end of line
                dest_f.write(self._text)
                self._status = NORMAL_CODE
                return True
            return False  # Stuff after comment so check by character
        # Whole line in comment without end
        dest_f.write(self._text)
        return True

    def _process_line_comment_start(self, dest_f):
        """ Processes a line known assumed to contain a /* but not know where

        There is aslo the assumption that the start status is not COMMENT

        :param dest_f:
        :return:
        """
        stripped = self._text.strip()
        if stripped.startswith("/*"):
            self._previous_status = self._status
            self._status = COMMENT
            # Comment start so now check for comment end
            return self._process_line(dest_f)
        # Stuff before comment so check by char
        return False  # More than one possible end so check by char

    def _process_line_in_log(self, dest_f):
        stripped = self._text.strip()
        if stripped.startswith("//"):
            # Just a comment line so write and move on
            dest_f.write(self._text)
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
        self._write_log_method(dest_f)
        self._status = NORMAL_CODE
        return True

    def _process_line_in_log_close_bracket(self, dest_f):
        stripped = self._text.strip()
        if stripped[0] == ";":
            if stripped == ";":
                self._log_full += (";")
                self._log_lines += 1
                self._write_log_method(dest_f)
                self._status = NORMAL_CODE
                return True
            else:
                return False

        elif stripped.startswith("//"):
            # Just a comment line so write and move on
            dest_f.write(self._text)
            return True

        else:
            # so not a closing bracket so set status back
            self._status = IN_LOG
            return self._process_line_in_log(dest_f)

    def _process_line_normal_code(self, dest_f):
        # Fast check
        if "log_" not in self._text:
            # No log start found
            dest_f.write(self._text)
            return True

        # Full slower check
        stripped = self._text.strip()
        match = LOG_START_REGEX.search(stripped)
        if not match:
            # No log start found after all
            dest_f.write(self._text)
            return True

        if match.start() > 0:
            if stripped.startswith("//"):
                # Just a comment line so write and move on
                dest_f.write(self._text)
                return True
            # Stuff before the log_start so check by character
            return False

        if LOG_START_REGEX.search(stripped, 1):
            # Second start found so check by character
            return False

        # remove whitespaces and save log command
        self._log_start = self._text.index(match.group(0))
        self._log = "".join(match.group(0).split())
        self._status = IN_LOG
        self._log_full = ""  # text saved in process_line_in_log
        self._log_lines = 0
        # Now check for the end of log command
        return self._process_line_in_log(dest_f)

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
                result += TOKEN
                result += match
            return result + '", {}'.format(self._message_id)

    def _write_log_method(self, dest_f):
        self._message_id += 1
        self._log_full = self._log_full.replace('""', '')
        try:
            original = STRING_REGEXP.search(self._log_full).group(0)
        except Exception:
            raise Exception("Unexpected line {} at {} in {}".format(
                self._log_full, self._line_num, self._src))
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
        with open(self._dict, 'a') as mess_f:
            # Remove commas from filenames for csv format
            # Remove start and end quotes from original
            mess_f.write("{},{} ({}: {}): ,{}\n".format(
                self._message_id, LEVELS[self._log],
                os.path.basename(self._src).replace(",", ";"),
                self._line_num + 1,
                original[1:-1]))

    def _process_chars(self, dest_f):
        pos = 0
        write_flag = 0
        while self._text[pos] != "\n":
            if self._status == COMMENT:
                if self._text[pos] == "*" and self._text[pos+1] == "/":
                    dest_f.write(self._text[write_flag:pos + 2])
                    pos = pos + 2
                    write_flag = pos
                    self._status = self._previous_status
                else:
                    pos = pos + 1
            elif self._text[pos] == "/":
                if self._text[pos+1] == "*":
                    if self._status == IN_LOG:
                        self._log_full += self._text[write_flag:pos].strip()
                        # NO change to self._log_lines as newline not removed
                    else:
                        dest_f.write(self._text[write_flag:pos])
                    write_flag = pos
                    pos = pos + 2  # leave the /* as not written
                    self._previous_status = self._status
                    self._status = COMMENT
                elif self._text[pos+1] == "/":
                    if self._status == IN_LOG:
                        self._log_full += self._text[write_flag:pos].strip()
                        # NO change to self._log_lines as newline not removed
                        dest_f.write(self._text[pos:])
                    else:
                        dest_f.write(self._text[write_flag:])
                    return  # Finished line
                else:
                    pos += 1

            elif self._text[pos] == '"':
                str_pos = pos + 1
                while self._text[str_pos] != '"':
                    if self._text[str_pos] == "\n":
                        raise Exception(
                            "Unclosed string literal in {} at line: {}".
                            format(self._file_name, self._line_num))
                    elif self._text[str_pos] == "\\":
                        if self._text[str_pos+1] == "\n":
                            raise Exception(
                                "Unclosed string literal in {} at line: {}".
                                format(self._file_name, self._line_num))

                        else:
                            str_pos += 2  # ignore next char which may be a "
                    else:
                        str_pos += 1
                pos = str_pos + 1
                continue

            elif self._status == IN_LOG:
                if self._text[pos] == ")":
                    match = LOG_END_REGEX.match(self._text[pos:])
                    if match:
                        # include the end
                        pos = pos + len(match.group(0))
                        self._log_full += self._text[write_flag:pos].strip()
                        self._status = NORMAL_CODE
                        if self._text[pos:].strip():  # Stuff left
                            write_flag = pos
                            # self._log_lines not changed as no newline
                            self._write_log_method(dest_f)
                        else:
                            self._log_lines += 1
                            self._write_log_method(dest_f)
                            return  # Finished line
                    else:
                        # not the require ); so continue
                        pos += 1
                else:
                    pos += 1

            elif self._status == IN_LOG_CLOSE_BRACKET:
                stripped = self._text.strip()
                if stripped[0] == ";":
                    self._log_full += (";")
                    self._write_log_method(dest_f)
                    pos = self._text.index(";") + 1
                    write_flag == pos
                    self._status = NORMAL_CODE
                else:
                    # Save the ) as not part of the end
                    self._status = IN_LOG

            elif self._text[pos] == "l":
                match = LOG_START_REGEX.match(self._text[pos:])
                if match:
                    self._log_start = self._text.index(match.group(0))
                    self._log = "".join(match.group(0).split())
                    self._status = IN_LOG
                    self._log_full = ""  # text saved after while
                    self._log_lines = 0
                    dest_f.write(self._text[write_flag:pos])
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
            self._log_full += self._text[write_flag:].strip()
            self._log_lines += 1
        else:
            dest_f.write(self._text[write_flag:])

    def unique_src(self):
        pos = 0
        last_sep = 0
        while pos < len(self._src) and pos < len(self._dest) \
                and self._src[pos] == self._dest[pos]:
            if self._src[pos] == os.path.sep:
                last_sep = pos + 1
            pos += 1
        return self._src[last_sep:]

    def get_message_id(self):
        filename = os.path.basename(self._src)

        # If the range_file does not exist create it and use range_start
        if not os.path.exists(self._range_file):
            with open(self._range_file, 'w') as log_ranges_file:
                log_ranges_file.write("AUTOGENERATED DO NOT EDIT\n")
                log_ranges_file.write("{} {}\n".format(
                    self._range_start, filename))
            return self._range_start

        # Check if the file is ranged or find highest range so far
        highest_found = self._range_start
        with open(self._range_file, 'r') as log_ranges_file:
            data_lines = iter(log_ranges_file)
            next(data_lines)  # Ignore do not edit
            for line in data_lines:
                parts = line.split(" ", 1)
                if filename.strip() == parts[1].strip():
                    return int(parts[0])
                else:
                    highest_found = max(highest_found, int(parts[0]))

        # Go one step above best found
        new_start = highest_found + MAX_LOG_PER_FILE

        # Append to range file in case rebuilt without clean
        with open(self._range_file, 'a') as log_ranges_file:
            log_ranges_file.write("{} {}\n".format(new_start, filename))
        return new_start

    @staticmethod
    def convert(src, dest, dict, range_start):
        convertor = FileConvertor(src, dest, dict, range_start)
        return convertor.run()


if __name__ == '__main__':
    src = sys.argv[1]
    dest = sys.argv[2]
    dict = sys.argv[3]
    range_start = int(sys.argv[4])
    FileConvertor.convert(src, dest, dict, range_start)
