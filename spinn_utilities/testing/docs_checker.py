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
from typing import cast, Optional, Set

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
        "__check_returns",
        "__error_level", "__file_path", "__file_errors", "__functions_errors"]

    def __init__(
            self, check_init: bool, check_short: bool,
            check_params: bool, check_returns: Optional[bool] = False) -> None:
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
        :param check_returns: Flag to trigger checking of return annotations
            when not a property
        """
        self.__error_level = ERROR_NONE
        self.__check_init = check_init
        self.__check_params = check_params
        self.__check_short = check_short
        self.__check_returns = check_returns
        self.__file_path = "None"
        self.__file_errors = 0
        self.__functions_errors = 0

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
        try:
            ast_tree = ast.parse(raw_tree, type_comments=True)
        except SyntaxError as ex:
            raise SyntaxError(f"{ex.msg} of {file_path}") from ex
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef):
                self.check_function(node)

    def _check_function(self, node: ast.FunctionDef) -> str:
        """
        Check the documentation in this function.

        :return: The error string. Empty if all ok
        """
        if self.__error_level > ERROR_FILE:
            self.__error_level = ERROR_FILE
        _docs = ast.get_docstring(node)
        if _docs is None:
            # pylint does not require init to have docs
            if node.name == "__init__" and self.__check_init:
                return "missing docstring"
            return ""
        else:
            docs = cast(str, _docs)

        docstring = docstring_parser.parse(docs)
        error = self._check_params(node, docstring)

        if node.name.startswith("_"):
            # these are not included by readthedocs so less important
            return error
        error += self._check_docs(docs)

        if self.is_property(node):
            if self.__check_short:
                if docstring.short_description is None:
                    error += "No short description provided."
        elif self.__check_returns:
            if self.has_returns(node):
                if len(docstring.many_returns) == 0:
                    error += "No returns"

        return error

    def check_function(self, node: ast.FunctionDef) -> None:
        """
        Check the documentation in this function.
        """
        if self.__error_level > ERROR_FILE:
            self.__error_level = ERROR_FILE
        error = self._check_function(node)

        if error:
            if self.__error_level < ERROR_FILE:
                print(f"{self.__file_path}")
                self.__file_errors += 1
            self.__error_level = ERROR_FILE
            print(f"\t{node.name} {node.lineno}")
            print(f"\t{error}")
            self.__functions_errors += 1

    def is_property(self, node: ast.FunctionDef) -> bool:
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "property":
                return True
        return False

    def has_returns(self, node: ast.FunctionDef) -> bool:
        returns = node.returns
        if isinstance(returns, ast.Constant):
            if returns.value is None:
                return False
        return True

    def _check_params(self, node: ast.FunctionDef,
                      docstring: docstring_parser.common.Docstring) -> str:
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

        return error

    def _check_docs(self, docs: str) -> str:
        error = ""

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

        return error

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
            raise AssertionError(
                f"The documentation checker failed "
                f"on {self.__functions_errors} errors "
                f"in {self.__file_errors} files")


if __name__ == "__main__":
    checker = DocsChecker(
        check_returns = True, check_init=False, check_short=False, check_params=False)
    #checker.check_dir("/home/brenninc/spinnaker/SpiNNUtils/")
    checker.check_file("/home/brenninc/spinnaker/SpiNNUtils/spinn_utilities/classproperty.py")
