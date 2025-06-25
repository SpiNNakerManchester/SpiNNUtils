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

import ast
import os
import sys
from typing import cast, Set

import docstring_parser

ERROR_NONE = 0
ERROR_OTHER = ERROR_NONE + 1
ERROR_FILE = ERROR_OTHER + 1


class DocsChecker(object):
    """
    A utility class to check the docs strings for our rules.

    As we use type annotations doc strings should not have types.
    At best they are the same otherwise they are wrong.

    We check that all documented params are actually ones used.
    The inverse is not checked as a good param name is often enough

    """

    __slots__ = [
        "__check_init", "__check_short", "__check_params",
        "__error_level", "__file_path"]

    def __init__(self, check_init: bool, check_short: bool,
                 check_params: bool) -> None:
        """
        Sets up the doc checker.

        Which functions need to be documented is left to pylint to check.
        Currently, that is public methods and public methods of public classes.
        pylint does not insist init methods are documented.

        :param check_init: flag to trigger checking of __init__ methods.
            If True all init methods must have all params documented
            Descriptions not required on __init__ files
        :param check_short: Flag to trigger checking of description.
            If there is a documentation (except for __init__)
            this must include a short description
        :param check_params: Flag to trigger checking of param docs.
            This will not check if all params are documented.
            However, if a param is documented it must include a description.
        """
        self.__error_level = ERROR_NONE
        self.__check_init = check_init
        self.__check_params = check_params
        self.__check_short = check_short
        self.__file_path = "None"

    def check_dir(self, dir_path: str) -> None:
        """
        Checks all py files in this directory including subdirectories.
        """
        for root, dir_names, files in os.walk(dir_path):
            dir_names.sort()
            files.sort()
            for file_name in files:
                if file_name.endswith(".py"):
                    self.check_file(os.path.join(root, file_name))

    def check_file(self, file_path: str) -> None:
        """
        Check the documentation in this file.
        """
        if self.__error_level > ERROR_OTHER:
            self.__error_level = ERROR_OTHER
        self.__file_path = file_path
        with open(file_path, "r", encoding="utf-8") as file:
            raw_tree = file.read()
        ast_tree = ast.parse(raw_tree, type_comments=True)
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef):
                self.check_function(node)

    def check_function(self, node: ast.FunctionDef) -> None:
        """
        Check the documentation in this function.
        """
        if self.__error_level > ERROR_FILE:
            self.__error_level = ERROR_FILE
        docs = ast.get_docstring(node)
        if docs is None and node.name != "__init__":
            return

        # docstring_parser.parse does handle None it is annotated incorrectly
        docstring = docstring_parser.parse(cast(str, docs))
        error = ""

        param_names = self.get_param_names(node)
        for param in docstring.params:
            if param.arg_name not in param_names:
                error += f"{param.arg_name}: is incorrect "
            elif param.type_name:
                error += f"{param.arg_name}: is typed "
            elif not param.description:
                if self.__check_params:
                    error += f"{param.arg_name}: is blank "

        if node.name == "__init__":
            if len(docstring.params) != len(param_names):
                if self.__check_init:
                    error += "Missing params"
        else:
            if docstring.short_description is None:
                if self.__check_short:
                    error += "No short description provided."

        if docs is not None:
            for key in [":type", ":rtype"]:
                if key in docs:
                    error += f"found {key} "
            index = sys.maxsize
            for key in [":param", ":return", ":raises"]:
                if key in docs:
                    key_index = docs.index(key)
                    if key_index < index:
                        index = key_index
            if index < sys.maxsize:
                while index > 1 and docs[index-1] in [" ", "\t"]:
                    index -= 1
                if index >= 2:
                    if docs[index-2: index] != "\n\n":
                        error += "Missing blank line after description"

        if error:
            if self.__error_level < ERROR_FILE:
                print(f"{self.__file_path}")
            self.__error_level = ERROR_FILE
            print(f"\t{node.name} {node.lineno}")
            print(f"\t{error}")

    def get_param_names(self, node: ast.FunctionDef) -> Set[str]:
        """
        Gets the names of the parameters found in the abstract syntax tree.

        These are the ones actually declared.
        """
        param_names: Set[str] = set()
        for arg in node.args.args:
            param_names.add(arg.arg)
        for arg in node.args.kwonlyargs:
            param_names.add(arg.arg)
        if node.args.vararg:
            param_names.add(node.args.vararg.arg)
        if node.args.kwarg:
            param_names.add(node.args.kwarg.arg)

        return param_names

    def check_no_errors(self) -> None:
        """
        Checks that there are no errors found.

        Does not run any checks just check status after they are run

        :raises AssertionError: If any previous check found an error
        """
        if self.__error_level > ERROR_NONE:
            raise AssertionError("The documentation checker failed")


if __name__ == "__main__":
    checker = DocsChecker(
        check_init=False, check_short=False, check_params=False)
    checker.check_file("")
