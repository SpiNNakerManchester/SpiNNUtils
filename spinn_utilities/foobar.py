# Copyright (c) 2025 The University of Manchester
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

def public_no_class() -> None:
    print(1)

def _protected_no_class() -> None:
    print(2)

def __private_no_class() -> None:
    print(3)


class Foo(object):
    def public(self) -> None:
        self._protected()

    def _protected(self) -> None:
        self.__private()

    def __private(self) -> None:
        print(4)


class _Bar(object):
    def public(self) -> None:
        self._protected()

    def _protected(self) -> None:
        self.__private()

    def __private(self) -> None:
        print(5)


if __name__ == "__main__":
    public_no_class()
    _protected_no_class()
    __private_no_class()
    f = Foo()
    f.public()
    b = _Bar()
    b.public()