# Copyright (c) 2026 The University of Manchester
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

import ast
import os


class AnyChecker:
    """
    Checks a directory for imports of "Any"

    This is intended to find from typing import Any
    but actually just looks for the "Any"

    Can be provided exceptions
    """

    def __init__(self, dir_path: str,
                 exceptions: list[str] | None = None) -> None:
        """
        :param dir_path: Path to the top level directory
        """
        self.__dir_path = dir_path
        self.__all_errors = 0
        if exceptions:
            self.__exceptions = exceptions
        else:
            self.__exceptions = []
            # temp values until set on check_file
        self.__filepath = "TOBESET"

    def _check_file(self, filepath: str) -> None:
        with open(filepath, "r", encoding="utf-8") as file:
            raw_tree = file.read()
        try:
            ast_tree = ast.parse(raw_tree, type_comments=True)
        except SyntaxError as ex:
            raise SyntaxError(f"{ex.msg} of {filepath}") from ex

        for node in ast.walk(ast_tree):
            # only import nodes are of interest
            if not isinstance(node, ast.ImportFrom):
                continue

            # check if the import is from an init file
            module = node.module
            assert module is not None
            for name in node.names:
                if name.name == "Any":
                    if self.__all_errors == 0:
                        print("Import Any found outside exceptions")
                    self.__all_errors += 1
                    print(filepath)

    def check_dir(self) -> int:
        """
        Checks the directory

        :return: Number of errors found
        """
        for root, _, files in os.walk(self.__dir_path):
            for file_name in files:
                if (file_name.endswith(".py") and file_name
                        not in self.__exceptions):
                    self._check_file(os.path.join(root, file_name))
        return self.__all_errors


if __name__ == "__main__":
    exceptions: list[str] = []
    dir_checker = AnyChecker("PATH_HERE",
                             exceptions)
    errors = dir_checker.check_dir()
    if errors:
        raise AssertionError(errors)
