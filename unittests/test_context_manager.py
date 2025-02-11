# Copyright (c) 2020 The University of Manchester
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

from spinn_utilities.abstract_context_manager import AbstractContextManager


class CM(AbstractContextManager):
    def __init__(self) -> None:
        self.state = "open"

    def close(self) -> None:
        self.state = "closed"


class CMTestExn(Exception):
    """ Just an exception different from all others for testing. """


def test_acm_with_success() -> None:
    states = []
    cm = CM()
    states.append(cm.state)
    with cm:
        states.append(cm.state)
    states.append(cm.state)
    assert states == ["open",  "open", "closed"]
