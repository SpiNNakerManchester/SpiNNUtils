# Copyright (c) 2017-2018 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import inspect
import numpy
import os
import sys
import traceback


def all_modules(directory, prefix, remove_pyc_files=False):
    """ List all the python files found in this directory giving then the\
        prefix.

    Any file that ends in either ``.py`` or ``.pyc`` is assume a python module\
    and added to the result set.

    :param directory: path to check for python files
    :param prefix: package prefix top add to the file name
    :return: set of python package names
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
                results.update(all_modules(full_path, prefix + "." + module,
                               remove_pyc_files))
    return results

if (sys.version_info > (3, 0)):
    def check_module(module_name):
        __import__(module_name)
        module = sys.modules[module_name]
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                if inspect.getmodule(obj) == module:
                    if not inspect.isabstract(obj):
                        argspec = inspect.getfullargspec(obj.__new__)
                        if argspec[0] == ["type"]:
                            if numpy.ndarray in inspect.getmro(obj):
                                print("skipping {} as it is a numpy.ndarray"
                                      "".format(name))
                            else:
                                obj.__new__(obj)
else:
    # Obj.__new__ does not work in python2 USE Python 3!
    def check_module(module_name):
        __import__(module_name)


def load_modules(
        directory, prefix, remove_pyc_files=False, exclusions=None,
        gather_errors=True):
    """ Loads all the python files found in this directory, giving them the\
        specified prefix

    Any file that ends in either ``.py`` or ``.pyc`` is assume a python module\
    and added to the result set.

    :param directory: path to check for python files
    :param prefix: package prefix top add to the file name
    :param remove_pyc_files: True if ``.pyc`` files should be deleted
    :param exclusions: a list of modules to exclude
    :param gather_errors:\
        True if errors should be gathered, False to report on first error
    :return: None
    """
    if exclusions is None:
        exclusions = []
    modules = all_modules(directory, prefix, remove_pyc_files)
    errors = list()
    for module_name in modules:
        if module_name in exclusions:
            print("SKIPPING " + module_name)
            continue
        print(module_name)
        #try:
        check_module(module_name)
        #except Exception:  # pylint: disable=broad-except
        #    if gather_errors:
        #        errors.append((module_name, sys.exc_info()))
        #    else:
        #        raise

    for module, (exc_type, exc_value, exc_traceback) in errors:
        print("Error importing {}:".format(module))
        for line in traceback.format_exception(
                exc_type, exc_value, exc_traceback):
            for line_line in line.split("\n"):
                if line_line:
                    print("  ", line_line.rstrip())
    if errors:
        raise Exception("Error when importing, starting at {}".format(prefix))


def load_module(
        name, remove_pyc_files=False, exclusions=None, gather_errors=True):
    """ Loads this modules and all its children.

    :param name: name of the modules
    :param remove_pyc_files: True if ``.pyc`` files should be deleted
    :param exclusions: a list of modules to exclude
    :param gather_errors:\
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
