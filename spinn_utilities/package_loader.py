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

import os
import sys
import traceback


def all_modules(directory, prefix, remove_pyc_files=False):
    """
    List all the python files found in this directory giving then the prefix.

    Any file that ends in either ``.py`` or ``.pyc`` is assume a python module
    and added to the result set.

    :param str directory: path to check for python files
    :param str prefix: package prefix top add to the file name
    :return: set of python package names
    :rtype: set(str)
    """
    results = set()
    for module in os.listdir(directory):
        if module == "__init__.py":
            results.add(prefix)
        elif module == "__init__.pyc":
            results.add(prefix)
            if remove_pyc_files:  # pragma: no cover
                full_path = os.path.join(directory, module)
                print("Deleting: " + full_path)
                os.remove(full_path)
        elif module[-3:] == ".py":
            results.add(prefix + "." + module[:-3])
        elif module[-4:] == ".pyc":
            results.add(prefix + "." + module[:-4])
            if remove_pyc_files:  # pragma: no cover
                full_path = os.path.join(directory, module)
                print("Deleting: " + full_path)
                os.remove(full_path)
        elif module != "__pycache__":
            full_path = os.path.join(directory, module)
            if os.path.isdir(full_path):
                results.update(all_modules(
                    full_path, prefix + "." + module, remove_pyc_files))
    return results


def load_modules(
        directory, prefix, remove_pyc_files=False, exclusions=None,
        gather_errors=True):
    """
    Loads all the python files found in this directory, giving them the
    specified prefix.

    Any file that ends in either ``.py`` or ``.pyc`` is assume a python module
    and added to the result set.

    :param str directory: path to check for python files
    :param str prefix: package prefix top add to the file name
    :param bool remove_pyc_files: True if ``.pyc`` files should be deleted
    :param list(str) exclusions: a list of modules to exclude
    :param bool gather_errors:
        True if errors should be gathered, False to report on first error
    :return: None
    """
    if exclusions is None:
        exclusions = []
    modules = all_modules(directory, prefix, remove_pyc_files)
    errors = list()
    for module in modules:
        if module in exclusions:
            print("SKIPPING " + module)
            continue
        print(module)
        try:
            __import__(module)
        except Exception:  # pylint: disable=broad-except
            if gather_errors:
                errors.append((module, sys.exc_info()))
            else:
                raise

    for module, (exc_type, exc_value, exc_traceback) in errors:
        print(f"Error importing {module}:")
        for line in traceback.format_exception(
                exc_type, exc_value, exc_traceback):
            for line_line in line.split("\n"):
                if line_line:
                    print("  ", line_line.rstrip())
    if errors:
        raise ImportError(f"Error when importing, starting at {prefix}")


def load_module(
        name, remove_pyc_files=False, exclusions=None, gather_errors=True):
    """
    Loads this modules and all its children.

    :param str name: name of the modules
    :param bool remove_pyc_files: True if ``.pyc`` files should be deleted
    :param list(str) exclusions: a list of modules to exclude
    :param bool gather_errors:
        True if errors should be gathered, False to report on first error
    :return: None
    """
    if exclusions is None:
        exclusions = []
    module = __import__(name)
    path = module.__file__
    directory = os.path.dirname(path)
    load_modules(directory, name, remove_pyc_files, exclusions, gather_errors)


if __name__ == '__main__':  # pragma: no cover
    load_module("spinn_utilities", True)
