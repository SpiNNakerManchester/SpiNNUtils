# Copyright (c) 2017-2018 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class MultipleValuesException(Exception):

    def __init__(self, key=None, value1=None, value2=None):
        if key is None:
            msg = "Multiple values found"
        else:
            msg = "Multiple values found for key {}".format(key)
        if value1 is not None and value2 is not None:
            msg += " values found include {} and {}".format(value1, value2)
        super().__init__(msg)
