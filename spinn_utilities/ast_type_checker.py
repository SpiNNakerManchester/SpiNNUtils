# Copyright (c) 2024 The University of Manchester
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

import spinn_utilities
from spinn_utilities.exceptions import ConfigException


class AstTypeChecker(object):

    def __init__(self, directory: str):
        if not os.path.isdir(directory):
            raise ConfigException(f"Unable find {directory}")
        self._directory = directory
        self._pyfile = "Not Yet Set"
        self._errors_found = 0

    def check_directory(self):
        for root, _, files in os.walk(self._directory):
            for file_name in files:
                #if file_name in exceptions:
                #    pass
                if file_name.endswith(".py"):
                    self._pyfile = os.path.join(root, file_name)
                    self._check_python_file()

    def _check_python_file(self):
        with open(self._pyfile, "rt") as file:
            tree = ast.parse(file.read(), filename=self._pyfile)
        self._check_functions(tree.body)

    def _check_functions(self, body: ast.ImportFrom):
        for part in body:
            if isinstance(part, ast.FunctionDef):
                # print(ast.dump(func))
                arguments = part.args.args
                returns = part.returns
                if returns is None and len(arguments) == 0:
                    print(f"{self._python_name()}:{part.lineno} {part.name} "
                          "has no return type or arguments")
                    self._errors_found += 1
                for arg in arguments:
                    if arg.arg not in ["self", "cls"]:
                        annotation = arg.annotation
                        if annotation is None:
                            print(f"{self._python_name()}:{part.lineno} "
                                  f"{part.name}:{arg.arg} has no type")
                            self._errors_found += 1
                self._check_functions(part.body)
            elif isinstance(part, ast.ClassDef):
                self._check_functions(part.body)

    def _python_name(self):
        basename = os.path.basename(self._pyfile)
        return basename.split(".")[0]

    def error_count(self) -> int:
        return self._errors_found

if __name__ == "__main__":
    spinn_utilities_dir = spinn_utilities.__path__[0]
    ast_type_checker = AstTypeChecker(spinn_utilities_dir)
    ast_type_checker.check_directory()
