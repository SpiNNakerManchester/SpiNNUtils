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


class MultipleValuesException(Exception):
    """
    Raised when there more than one value found unexpectedly.
    """

    def __init__(self, key, value1, value2):
        if key is None:
            msg = "Multiple values found"
        else:
            msg = f"Multiple values found for key {key}"
        if value1 is not None and value2 is not None:
            msg += f" values found include {value1} and {value2}"
        super().__init__(msg)
