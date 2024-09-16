# Copyright (c) 2018 The University of Manchester
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

import sys


class IndexIsValue(object):
    """
    Tiny support class that implements ``object[x]`` by just returning
    ``x`` itself.

    Used for where you want a range from 1 to *N* but you don't know *N*.

    Clearly, operations that assume a finite list are *not* supported.
    """

    def __getitem__(self, key):
        return key

    def __len__(self):
        return sys.maxsize
