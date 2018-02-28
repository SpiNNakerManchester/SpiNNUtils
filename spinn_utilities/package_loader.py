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
            if remove_pyc_files:
                full_path = os.path.join(directory, module)
                print("Deleting: " + full_path)
                os.remove(full_path)
        elif module[-3:] == ".py":
            results.add(prefix + "." + module[:-3])
        elif module[-4:] == ".pyc":
            results.add(prefix + "." + module[:-4])
            if remove_pyc_files:
                full_path = os.path.join(directory, module)
                print("Deleting: " + full_path)
                os.remove(full_path)
        else:
            full_path = os.path.join(directory, module)
            if os.path.isdir(full_path):
                results.update(all_modules(full_path, prefix + "." + module,
                               remove_pyc_files))
    return results


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
    for module in modules:
        if module in exclusions:
            print("SKIPPING " + module)
            continue
        print(module)
        try:
            __import__(module)
        except Exception:
            if gather_errors:
                errors.append((module, sys.exc_info()))
            else:
                raise

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


if __name__ == '__main__':
    load_module("spinn_utilities", True)
