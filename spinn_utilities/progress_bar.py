# Copyright (c) 2017-2019 The University of Manchester
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

from __future__ import print_function, division
import logging
import sys
import math
import os
from spinn_utilities.overrides import overrides
from spinn_utilities import logger_utils

logger = logging.getLogger(__name__)


class ProgressBar(object):
    """ Progress bar for telling the user where a task is up to
    """
    MAX_LENGTH_IN_CHARS = 60

    TOO_MANY_ERROR = "Too many update steps in progress bar! " \
                     "This may be a sign that something else has gone wrong!"

    __slots__ = (
        "_number_of_things", "_currently_completed", "_destination",
        "_chars_per_thing", "_chars_done", "_string",
        "_step_character", "_end_character", "_in_bad_terminal"
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
        """ Update the progress bar by a given amount

        :param amount_to_add:
        :rtype: None
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
        print(
            "{}0%{}50%{}100%{}".format(
                self._end_character, " " * first_space,
                " " * second_space, self._end_character),
            end="", file=self._destination)
        if self._in_bad_terminal:
            print("", file=self._destination)
            print(" ", end="", file=self._destination)

    def _print_progress(self, length):
        chars_to_print = length
        if not self._in_bad_terminal:
            self._print_overwritten_line(self._end_character)
        else:
            chars_to_print = length - self._chars_done
        for _ in range(int(chars_to_print)):
            print(self._step_character, end='', file=self._destination)
        self._destination.flush()

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
        expected_chars_done = math.floor(
            self._currently_completed * self._chars_per_thing)
        if self._currently_completed == self._number_of_things:
            expected_chars_done = ProgressBar.MAX_LENGTH_IN_CHARS
        self._print_progress(expected_chars_done)
        self._chars_done = expected_chars_done

    def end(self):
        """ Close the progress bar, updating whatever is left if needed

        :rtype: None
        """
        difference = self._number_of_things - self._currently_completed
        self._currently_completed += difference
        self._check_differences()
        self._print_progress_done()

    def __repr__(self):
        return "<ProgressBar:{}>".format(self._string)

    def __enter__(self):
        """ Support method to use the progress bar as a context manager::

            with ProgressBar(...) as p:
                ...
                p.update()
                ...
                p.update()
                ...

        This method does not have any parameters because any parameters in the\
        with :samp:`ProgressBar(...)` call have been passed to\
        :py:meth:`__init__`

        Like :samp:`__new__` this method has to return self as in theory it\
        could pass back a different object. Welcome to Python.

        :return: The Progress bar
        """
        return self

    def __exit__(self, exty, exval, traceback):  # @UnusedVariable
        self.end()
        return False

    def over(self, collection, finish_at_end=True):
        """ Simple wrapper for the cases where the progress bar is being used\
            to show progress through the iteration over a single collection.\
            The progress bar should have been initialised to the size of the\
            collection being iterated over.

        :param collection:\
            The base collection (any iterable) being iterated over
        :param finish_at_end: \
            Flag to say if the bar should finish at the end of the collection
        :return: An iterable. Expected to be directly used in a for.
        """
        try:
            for item in collection:
                yield item
                self.update()
        finally:
            if finish_at_end:
                self.end()


class DummyProgressBar(ProgressBar):
    """ This is a dummy version of the progress bar that just stubs out the\
        internal printing operations with code that does nothing. It otherwise\
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
        return "<DummyProgressBar:{}>".format(self._string)


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
