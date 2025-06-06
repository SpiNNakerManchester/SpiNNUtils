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

from collections.abc import Sized
import logging
import math
import os
import sys
from types import TracebackType
from typing import Iterable, Optional, Type, TypeVar, Union

from typing_extensions import Literal, Self

from spinn_utilities.log import FormatAdapter
from spinn_utilities.overrides import overrides
from spinn_utilities import logger_utils


logger = FormatAdapter(logging.getLogger(__name__))
#: :meta private:
T = TypeVar("T")


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

    def __init__(self, total_number_of_things_to_do: Union[int, Sized],
                 string_describing_what_being_progressed: str,
                 step_character: str = "=", end_character: str = "|"):
        if isinstance(total_number_of_things_to_do, Sized):
            self._number_of_things = len(total_number_of_things_to_do)
        else:
            self._number_of_things = int(total_number_of_things_to_do)
        self._currently_completed = 0
        self._chars_per_thing = 1.0
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

    def update(self, amount_to_add: int = 1) -> None:
        """
        Update the progress bar by a given amount.

        :param amount_to_add:
        """
        if self._currently_completed + amount_to_add > self._number_of_things:
            logger_utils.error_once(logger, self.TOO_MANY_ERROR)
            return
        self._currently_completed += amount_to_add
        self._check_differences()

    def _print_overwritten_line(self, string: str) -> None:
        print("\r" + string, end="", file=self._destination)

    def _print_distance_indicator(self, description: str) -> None:
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

    def _print_distance_line(
            self, first_space: int, second_space: int) -> None:
        line = f"{self._end_character}0%{' ' * first_space}50%" \
               f"{' ' * second_space}100%{self._end_character}"
        print(line, end="", file=self._destination)

    def _print_progress(self, length: int) -> None:
        chars_to_print = length
        if not self._in_bad_terminal:
            self._print_overwritten_line(self._end_character)
        else:
            chars_to_print = length - self._chars_done

        for _ in range(int(chars_to_print)):
            self._print_progress_unit()
        self._destination.flush()

    def _print_progress_unit(self) -> None:
        print(self._step_character, end='', file=self._destination)

    def _print_progress_done(self) -> None:
        self._print_progress(ProgressBar.MAX_LENGTH_IN_CHARS)
        if not self._in_bad_terminal:
            print(self._end_character, file=self._destination)
        else:
            print("", file=self._destination)

    def _create_initial_progress_bar(self, description: str) -> None:
        if self._number_of_things == 0:
            self._chars_per_thing = ProgressBar.MAX_LENGTH_IN_CHARS
        else:
            self._chars_per_thing = \
                ProgressBar.MAX_LENGTH_IN_CHARS / self._number_of_things
        self._print_distance_indicator(description)
        self._print_progress(0)
        self._check_differences()

    def _check_differences(self) -> None:
        expected_chars_done = int(math.floor(
            self._currently_completed * self._chars_per_thing))
        if self._currently_completed == self._number_of_things:
            expected_chars_done = ProgressBar.MAX_LENGTH_IN_CHARS
        self._print_progress(expected_chars_done)
        self._chars_done = expected_chars_done

    def end(self) -> None:
        """
        Close the progress bar, updating whatever is left if needed.
        """
        difference = self._number_of_things - self._currently_completed
        self._currently_completed += difference
        self._check_differences()
        self._print_progress_done()

    def __repr__(self) -> str:
        return f"<ProgressBar:{self._string}>"

    def __enter__(self) -> Self:
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

    def __exit__(self, exc_type: Optional[Type], exc_val: Exception,
                 exc_tb: TracebackType) -> Literal[False]:
        self.end()
        return False

    def over(self, collection: Iterable[T],
             finish_at_end: bool = True) -> Iterable[T]:
        """
        Simple wrapper for the cases where the progress bar is being used
        to show progress through the iteration over a single collection.
        The progress bar should have been initialised to the size of the
        collection being iterated over.

        :param collection:
            The base collection (any iterable) being iterated over
        :param finish_at_end:
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
    """
    This is a dummy version of the progress bar that just stubs out the
    internal printing operations with code that does nothing. It otherwise
    fails in exactly the same way.
    """
    @overrides(ProgressBar._print_overwritten_line)
    def _print_overwritten_line(self, string: str) -> None:
        pass

    @overrides(ProgressBar._print_distance_indicator)
    def _print_distance_indicator(self, description: str) -> None:
        pass

    @overrides(ProgressBar._print_progress)
    def _print_progress(self, length: int) -> None:
        pass

    @overrides(ProgressBar._print_progress_done)
    def _print_progress_done(self) -> None:
        pass

    def __repr__(self) -> str:
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

    demo = DummyProgressBar(3, "Test Dummy")
    for prime in demo.over(_collection):
        sleep(0.1)
