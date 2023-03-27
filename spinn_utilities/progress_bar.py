# Copyright (c) 2017 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import defaultdict
from datetime import date
import logging
import math
import os
import sys
from spinn_utilities.config_holder import get_config_bool
from spinn_utilities.log import FormatAdapter
from spinn_utilities.overrides import overrides
from spinn_utilities import logger_utils
import spinn_utilities

logger = FormatAdapter(logging.getLogger(__name__))


class ProgressBar(object):
    """
    Progress bar for telling the user where a task is up to.
    """
    MAX_LENGTH_IN_CHARS = 60

    TOO_MANY_ERROR = (
        "Too many update steps in progress bar! "
        "This may be a sign that something else has gone wrong!")

    __slots__ = (
        "_number_of_things", "_currently_completed", "_destination",
        "_chars_per_thing", "_chars_done", "_string",
        "_step_character", "_end_character", "_in_bad_terminal",
    )

    def __init__(self, total_number_of_things_to_do,
                 string_describing_what_being_progressed,
                 step_character="=", end_character="|"):
        try:
            self._number_of_things = int(total_number_of_things_to_do)
        except TypeError:

            # Might be dealing with general iterable; better not be infinite
            self._number_of_things = len(list(total_number_of_things_to_do))

        self._currently_completed = 0
        self._chars_per_thing = None
        self._chars_done = 0
        self._string = string_describing_what_being_progressed
        self._destination = sys.stderr
        self._step_character = step_character
        self._end_character = end_character

        # Determine if we are in a "bad" terminal i.e. one that doesn't handle
        # carriage return correctly
        self._in_bad_terminal = "PROGRESS_GOOD_TERMINAL" not in os.environ

        self._create_initial_progress_bar(
            string_describing_what_being_progressed)

    def update(self, amount_to_add=1):
        """
        Update the progress bar by a given amount.

        :param amount_to_add:
        """
        if self._currently_completed + amount_to_add > self._number_of_things:
            logger_utils.error_once(logger, self.TOO_MANY_ERROR)
            return
        self._currently_completed += amount_to_add
        self._check_differences()

    def _print_overwritten_line(self, string):
        print("\r" + string, end="", file=self._destination)

    def _print_distance_indicator(self, description):
        if description is not None:
            print(description, file=self._destination)

        # Find the mid point
        mid_point = ProgressBar.MAX_LENGTH_IN_CHARS // 2

        # The space between 0% and 50% is the mid-point minus the width of
        # 0% and ~half the width of 50%
        first_space = mid_point - 4

        # The space between 50% and 100% is the mid-point minus the rest of
        # the width of 50% and the width of 100%
        second_space = mid_point - 5

        # Print the progress bar itself
        self._print_distance_line(first_space, second_space)
        if self._in_bad_terminal:
            print("", file=self._destination)
            print(" ", end="", file=self._destination)

    def _print_distance_line(self, first_space, second_space):
        line = "{}0%{}50%{}100%{}".format(
            self._end_character, " " * first_space, " " * second_space,
            self._end_character)
        print(line, end="", file=self._destination)

    def _print_progress(self, length):
        chars_to_print = length
        if not self._in_bad_terminal:
            self._print_overwritten_line(self._end_character)
        else:
            chars_to_print = length - self._chars_done

        for _ in range(int(chars_to_print)):
            self._print_progress_unit(chars_to_print)
        self._destination.flush()

    def _print_progress_unit(self, chars_to_print):
        # pylint: disable=unused-argument
        print(self._step_character, end='', file=self._destination)

    def _print_progress_done(self):
        self._print_progress(ProgressBar.MAX_LENGTH_IN_CHARS)
        if not self._in_bad_terminal:
            print(self._end_character, file=self._destination)
        else:
            print("", file=self._destination)

    def _create_initial_progress_bar(self, description):
        if self._number_of_things == 0:
            self._chars_per_thing = ProgressBar.MAX_LENGTH_IN_CHARS
        else:
            self._chars_per_thing = \
                ProgressBar.MAX_LENGTH_IN_CHARS / self._number_of_things
        self._print_distance_indicator(description)
        self._print_progress(0)
        self._check_differences()

    def _check_differences(self):
        expected_chars_done = int(math.floor(
            self._currently_completed * self._chars_per_thing))
        if self._currently_completed == self._number_of_things:
            expected_chars_done = ProgressBar.MAX_LENGTH_IN_CHARS
        self._print_progress(expected_chars_done)
        self._chars_done = expected_chars_done

    def end(self):
        """
        Close the progress bar, updating whatever is left if needed.
        """
        difference = self._number_of_things - self._currently_completed
        self._currently_completed += difference
        self._check_differences()
        self._print_progress_done()

    def __repr__(self):
        return f"<ProgressBar:{self._string}>"

    def __enter__(self):
        """
        Support method to use the progress bar as a context manager::

            with ProgressBar(...) as p:
                ...
                p.update()
                ...
                p.update()
                ...

        This method does not have any parameters because any parameters in the
        with :samp:`ProgressBar(...)` call have been passed to
        :py:meth:`__init__`

        Like :samp:`__new__` this method has to return self as in theory it
        could pass back a different object. Welcome to Python.

        :return: The Progress bar
        """
        return self

    def __exit__(self, exty, exval, traceback):  # @UnusedVariable
        self.end()
        return False

    def over(self, collection, finish_at_end=True):
        """
        Simple wrapper for the cases where the progress bar is being used
        to show progress through the iteration over a single collection.
        The progress bar should have been initialised to the size of the
        collection being iterated over.

        :param ~collections.abc.Iterable collection:
            The base collection (any iterable) being iterated over
        :param bool finish_at_end:
            Flag to say if the bar should finish at the end of the collection
        :return: An iterable. Expected to be directly used in a for.
        :rtype: ~collections.abc.Iterable
        """
        try:
            for item in collection:
                yield item
                self.update()
        finally:
            if finish_at_end:
                self.end()

    def __new__(cls, *args, **kwargs):  # @UnusedVariable
        # pylint: disable=unused-argument
        c = cls
        if _EnhancedProgressBar._enabled:
            if get_config_bool("Mode", "I_have_a_sense_of_humour"):
                c = _EnhancedProgressBar
            else:
                _EnhancedProgressBar._enabled = False
        return super().__new__(c)


class _EnhancedProgressBar(ProgressBar):
    """
    Nothing to see here.
    """

    _line_no = 0
    _seq_id = 0
    _step_characters = defaultdict(list)
    _enabled = False
    _DATA_FILE = "progress_bar.txt"

    def _print_progress_unit(self, chars_to_print):
        song_line = self.__line
        if not self._in_bad_terminal:
            print(song_line[0:self._chars_done + chars_to_print],
                  file=self._destination)
        else:
            print(song_line[self._chars_done:self._chars_done + 1],
                  end='', file=self._destination)
            self._chars_done += 1

    def _print_progress_done(self):
        self._print_progress(ProgressBar.MAX_LENGTH_IN_CHARS)
        if not self._in_bad_terminal:
            self._print_overwritten_line(self._end_character)
            for _ in range(ProgressBar.MAX_LENGTH_IN_CHARS):
                print(self._step_character, end='', file=self._destination)
            print(self._end_character, file=self._destination)
        else:
            print("", file=self._destination)
        self.__next_line()

    @property
    def __line(self):
        return _EnhancedProgressBar._step_characters[
            _EnhancedProgressBar._seq_id][_EnhancedProgressBar._line_no]

    @classmethod
    def __next_line(cls):
        if cls._line_no + 1 >= len(cls._step_characters[cls._seq_id]):
            cls._line_no = 0
        else:
            cls._line_no += 1

    @classmethod
    def init_once(cls):
        cls._enabled = False
        # read in the songs once for performance reasons
        path = os.path.join(
            os.path.dirname(os.path.realpath(spinn_utilities.__file__)),
            cls._DATA_FILE)
        try:
            with open(path, encoding="utf-8") as reader:
                lines = reader.readlines()

            # turn into array of songs, skipping comments and blanks
            for line in lines:
                if line.startswith("#") or line.strip() == "":
                    continue
                bits = line.split(":")
                if len(bits) != 3:
                    # Bad data! Abort!
                    break
                cls._step_characters[bits[0]].append(bits[1])

            # clean up lines so that spaces are still visible
            for _seq_id in cls._step_characters:
                step = cls._step_characters[_seq_id]
                for _line_no in range(len(step)):
                    step[_line_no] = step[_line_no].replace(" ", "_")

            # verify that its a special day
            cls._enabled = (
                    date.today().strftime("%m%d") in cls._step_characters)
        except IOError:
            cls._seq_id = 0
        finally:
            cls._line_no = 0
            if cls._enabled:
                cls._seq_id = date.today().strftime("%m%d")
            else:
                # To allow testing on a none special day
                cls._seq_id = "test"


# Perform one-time initialisation
_EnhancedProgressBar.init_once()


class DummyProgressBar(ProgressBar):
    """
    This is a dummy version of the progress bar that just stubs out the
    internal printing operations with code that does nothing. It otherwise
    fails in exactly the same way.
    """
    @overrides(ProgressBar._print_overwritten_line)
    def _print_overwritten_line(self, string):
        pass

    @overrides(ProgressBar._print_distance_indicator)
    def _print_distance_indicator(self, description):
        pass

    @overrides(ProgressBar._print_progress)
    def _print_progress(self, length):
        pass

    @overrides(ProgressBar._print_progress_done)
    def _print_progress_done(self):
        pass

    def __repr__(self):
        return f"<DummyProgressBar:{self._string}>"


if __name__ == "__main__":  # pragma: no cover
    from time import sleep
    demo = ProgressBar(
        5, "Progress Bar Demonstration", step_character="-", end_character="!")
    for _ in range(5):
        sleep(1)
        demo.update()
    demo.end()
    demo = ProgressBar(30, "Progress Bar Demonstration")
    for _ in range(30):
        sleep(0.1)
        demo.update()
    demo.end()

    _collection = [2, 3, 5, 7, 11, 13, 17]
    demo = ProgressBar(_collection, "Demo over a few primes")
    for prime in demo.over(_collection):
        sleep(0.1)
