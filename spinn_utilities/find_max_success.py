# Copyright (c) 2019 The University of Manchester
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


def find_max_success(max_possible, check):
    """
    Finds the maximum value that will pass the check

    :param max_possible: The maximum value that should be tested.
    :type max_possible: int
    :param check: A boolean function that given an int value returns
        True for every value up and including the cut-off and
        False for every value greater than the cut-off
    :type check: ~typing.Callable[[int], bool]
    :return: The highest value that returns true for the check
        but is not more than the max_possible
    """
    # Check the max to avoid multiple steps if that works
    if check(max_possible):
        return max_possible
    return search_for_max_success(0, max_possible, check)


def search_for_max_success(best_success, min_fail, check):
    """
    Finds the maximum value in the range that pass the check

    :param best_success: A minimum value that needs not be tested because it
        is either known to succeed or is a flag for total failure.
        Can be negative
    :type best_success: int
    :param min_fail: A maximum value that needs not be tested because it
        is either known to fail or one more than the maximum interesting value
        but must be greater than best_success but may also be negative
    :type min_fail: int
    :param check: A boolean function that given an int value returns
        True for every value up and including the cut-off and
        False for every value greater than the cut-off
    :type check: ~typing.Callable[[int], bool]
    :return: The highest value that returns true in the range between
        `best_success` and `min_fail` (both exclusive ends) or `best_success`
        if the whole range fails or is empty.
    """
    # Check if there are still values in the middle to check
    if best_success >= min_fail - 1:
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
