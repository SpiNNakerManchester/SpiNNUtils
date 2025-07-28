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
        "__check_properties", "__check_returns",
        "__error_level", "__file_path", "__file_errors",
        "__functions_errors"]

    def __init__(
            self, *, check_init: bool = True, check_short: bool = True,
            check_params: bool = True, check_properties: bool = True,
            check_returns: bool = True) -> None:
        """
        Sets up the doc checker.

        Which functions need to be documented is left to pylint to check.
        Currently, that is public methods and public methods of public classes.
        pylint does not insist init methods are documented.

        :param check_init: flag to trigger checking of __init__ methods.
            If True all init methods must have all params documented
            Descriptions not allowed on __init__ files
            as they should be on the class only.
        :param check_short: Flag to trigger checking of a description.
            For public (None init) methods (except setters) with no return
            there must be a short description
        :param check_params: Flag to trigger checking of params.
            If any param is listed all must be.
            The param does not need to be documented.
        :param check_properties: Flag to trigger checking of Properties
            They must include a description.
            They should not have a return annotation
        :param check_returns: Flag to trigger checking of return annotations
            when not a property
        """
        self.__error_level = ERROR_NONE
        self.__check_init = check_init
        self.__check_params = check_params
        self.__check_properties = check_properties
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
        """
        if self.__error_level > ERROR_FILE:
            self.__error_level = ERROR_FILE
        _docs = ast.get_docstring(node)
        if _docs is None:
            # pylint does not require init to have docs
            if node.name == "__init__" and self.__check_init:
                param_names = self.get_param_names(node)
                if (len(param_names) > 0 and self.is_not_overload(node) and
                        not self._test_path()):
                    return "missing docstring"
            return ""
        else:
            docs = cast(str, _docs)

        docstring = docstring_parser.parse(docs)
        param_names = self.get_param_names(node)
        error = self._check_params_correct(param_names, docstring)

        if not self.has_returns(node) and len(docstring.many_returns) > 0:
            error += "Unexpected returns"

        if (node.name.startswith("_") or self._test_path() or
                self._overrides(node)):
            # these are not included by readthedocs so less important
            return error

        if node.name == "__init__":
            if self.__check_init:
                if len(docstring.params) != len(param_names):
                    error += "Missing params"
                if docstring.short_description is not None:
                    error += "Short description provided."
                if len(docstring.many_returns) > 0:
                    error += ("Unexpected returns")
        elif self.has_returns(node):
            if self.is_property(node):
                if self.__check_properties:
                    if docstring.short_description is None:
                        error += "No short description provided."
                    if len(docstring.many_returns) > 0:
                        error += "Unexpected returns"
                        if self.__check_params:
                            error += self._check_params_all_or_none(
                                param_names, docstring)
            else:
                if self.__check_returns:
                    if len(docstring.many_returns) == 0:
                        error += "No returns"
                if self.__check_params:
                    error += self._check_params_all_or_none(
                        param_names, docstring)
        else:
            if self.__check_short:
                if docstring.short_description is None:
                    error += "No short description provided."
            if self.__check_params:
                error += self._check_params_all_or_none(
                    param_names, docstring)

        error += self._check_blank_lines(docs)

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
        """
        :return: True if and only if there is a @property decorator
        """
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "property":
                return True
        return False

    def is_not_overload(self, node: ast.FunctionDef) -> bool:
        """
        :return: True if and only if there is NO @overload decorator
        """
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "overload":
                return False
        return True

    def has_returns(self, node: ast.FunctionDef) -> bool:
        """
        :return: True if and only if there is a return declared
        """
        returns = node.returns
        if isinstance(returns, ast.Constant):
            if returns.value is None:
                return False
        elif isinstance(returns, ast.Name):
            if returns.id == "Never":
                return False
        return True

    def _overrides(self, node: ast.FunctionDef) -> bool:
        """
        Detects the overrides annotation and the extend_docs is not False
        """
        for decorator in node.decorator_list:
            try:
                if (isinstance(decorator, ast.Call) and
                        isinstance(decorator.func, ast.Name) and
                        decorator.func.id == "overrides"):
                    for keyword in decorator.keywords:
                        if keyword.arg == "extend_doc":
                            value = cast(ast.Constant, keyword.value)
                            return bool(value.value)
                    return True
            except AttributeError:
                print(decorator)
        return False

    def _test_path(self) -> bool:
        """
        :returns: True if the path is likely for tests
        """
        test_paths = ["fec_integration_tests", "pacman_test_objects",
                      "tests", "unittests"]
        for test_path in test_paths:
            check = os.sep + test_path + os.sep
            if check in self.__file_path:
                return True
        return False

    def _check_params_correct(
            self, param_names: Set[str],
            docstring: docstring_parser.common.Docstring) -> str:
        """
        Checks that all params listed are used and not typed
        """
        error = ""
        for param in docstring.params:
            if param.arg_name not in param_names:
                error += f"{param.arg_name}: is incorrect "
            elif param.type_name:
                error += f"{param.arg_name}: is typed "
        return error

    def _check_params_all_or_none(
            self, param_names: Set[str],
            docstring: docstring_parser.common.Docstring) -> str:
        """
        Checks that either no or all params are listed
        """
        if len(docstring.params) == 0:
            return ""
        elif len(docstring.params) != len(param_names):
            return "Missing params"
        else:
            return ""

    def _check_blank_lines(self, docs: str) -> str:
        """
        Check there are blank lines where needed
        """
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

        :returns: Names of all parameter including normal and kwargs ones
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

        if "self" in param_names:
            param_names.remove("self")
        if "cls" in param_names:
            param_names.remove("cls")
        return param_names

    def check_no_errors(self) -> None:
        """
        Checks that there are no errors found.

        Does not run any checks just check status after they are run

        :raises AssertionError: If any previous check found an error
        """
        if self.__error_level > ERROR_NONE:
            raise AssertionError(
                f"The documentation checker found "
                f"{self.__functions_errors} errors "
                f"in {self.__file_errors} files")


if __name__ == "__main__":
    checker = DocsChecker(
        check_init=False,
        check_short=False,
        check_params=False,
        check_properties=False
    )
    # checker.check_dir("")
    checker.check_file("")
