from __future__ import print_function
import sys
import math


class ProgressBar(object):
    """ Progress bar for telling the user where a task is up to
    """
    MAX_LENGTH_IN_CHARS = 60

    __slots__ = (
        "_number_of_things", "_currently_completed", "_destination",
        "_chars_per_thing", "_last_update", "_chars_done", "_string",
        "_step_character"
    )

    def __init__(self, total_number_of_things_to_do,
                 string_describing_what_being_progressed,
                 step_character="="):
        try:
            self._number_of_things = int(total_number_of_things_to_do)
        except TypeError:
            # Might be dealing with general iterable; better not be infinite
            self._number_of_things = len(list(total_number_of_things_to_do))
        self._currently_completed = 0
        self._chars_per_thing = None
        self._last_update = 0
        self._chars_done = 0
        self._string = string_describing_what_being_progressed
        self._destination = sys.stderr
        self._step_character = step_character

        self._create_initial_progress_bar(
            string_describing_what_being_progressed)

    def update(self, amount_to_add=1):
        """ Update the progress bar by a given amount

        :param amount_to_add:
        :return:
        """
        self._currently_completed += amount_to_add
        self._check_differences()

    def _print_distance_indicator(self, description):
        print(description, file=self._destination)
        print("|0                           50%                         100%|",
              end="", file=self._destination)

    def _print_progress(self, length):
        print("\r|", end="", file=self._destination)
        for _ in range(int(length)):
            print(self._step_character, end='', file=self._destination)
        if self._currently_completed == self._number_of_things:
            print("|", file=self._destination)
        self._destination.flush()

    def _print_progress_done(self):
        print("", file=self._destination)

    def _create_initial_progress_bar(self, description):
        if self._number_of_things == 0:
            self._chars_per_thing = ProgressBar.MAX_LENGTH_IN_CHARS
        else:
            self._chars_per_thing = (ProgressBar.MAX_LENGTH_IN_CHARS /
                                     float(self._number_of_things))
        self._print_distance_indicator(description)
        self._print_progress(0)
        self._check_differences()

    def _check_differences(self):
        expected_chars_done = math.floor(self._currently_completed *
                                         self._chars_per_thing)
        if self._currently_completed == self._number_of_things:
            expected_chars_done = ProgressBar.MAX_LENGTH_IN_CHARS
        self._print_progress(expected_chars_done)
        self._chars_done = expected_chars_done

    def end(self):
        """ Close the progress bar, updating whatever is left if needed

        :return:
        """
        difference = self._number_of_things - self._currently_completed
        self._currently_completed += difference
        self._check_differences()
        self._print_progress_done()

    def __repr__(self):
        return "progress bar for {}".format(self._string)

    def __enter__(self):
        pass

    def __exit__(self, exty, exval, traceback):
        self.end()


if __name__ == "__main__":
    from time import sleep
    demo = ProgressBar(5, "Progress Bar Demonstration", step_character="-")
    for _ in range(5):
        sleep(1)
        demo.update()
