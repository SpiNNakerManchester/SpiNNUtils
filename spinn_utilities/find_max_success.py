# Copyright (c) 2019 The University of Manchester
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


def find_max_success(max_possible, check):
    """
    Finds the maximum value that will pass the check

    :param max_possible: The maximum value that should be tested.
    :type max_possible: int
    :param check: A boolean function that given an int value returns
        true for every value up and including the cutoff and
        false for every value greater than the cutoff
    :return: The highest value that returns true for the check
        but is not more than the max_possible
    """
    # Check the max to avoid multiple steps if that works
    if check(max_possible):
        return max_possible
    return search_for_max_success(0, max_possible, check)


def search_for_max_success(best_success, min_fail, check):
    """
    Finds the maximun value in the range that pass the check

    :param best_success: A minimum value that needs not be tested because it
        is either known to succeed or is a flag for total failure.
        Can be negative
    :type best_success: int
    :param min_fail: A maximum value that needs not be tested because it
        is either known to fail or one more than the maximum interesting value
        but must be greater than best_success but may also be negative
    :type min_fail: int
    :param check: A boolean function that given an int value returns
        true for every value up and including the cutoff and
        false for every value greater than the cutoff
    :return: The highest value that returns true in the range between
        best_success and min_fail (both exclusive ends) or best_success if the
        whole range fails or is empty.
    """
    # Check if there are still values in the middle to check
    if (best_success >= min_fail - 1):
        return best_success
    # Find the middle
    mid_point = (best_success + min_fail) // 2
    # Check the middle
    if check(mid_point):
        # Best it the middle or more
        return search_for_max_success(mid_point, min_fail, check)
    else:
        # Best it the less than the middle
        return search_for_max_success(best_success, mid_point, check)
