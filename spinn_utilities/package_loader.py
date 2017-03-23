import os


def all_modules(directory, prefix, remove_pyc_files=False):
    """
    List all the python files found in this directory giving then the prefix

    Any file that ends in either .py or .pyc is assume a python module
    and added to the result set

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
                print "Deleting: " + full_path
                os.remove(full_path)
        elif module[-3:] == ".py":
            results.add(prefix + "." + module[:-3])
        elif module[-4:] == ".pyc":
            results.add(prefix + "." + module[:-4])
            if remove_pyc_files:
                full_path = os.path.join(directory, module)
                print "Deleting: " + full_path
                os.remove(full_path)
        else:
            full_path = os.path.join(directory, module)
            if os.path.isdir(full_path):
                results.update(all_modules(full_path, prefix + "." + module,
                               remove_pyc_files))
    return results


def load_modules(directory, prefix, remove_pyc_files=False, exclusions=[]):
    """
    Loads all the python files found in this directory giving then the prefix

    Any file that ends in either .py or .pyc is assume a python module
    and added to the result set

    :param directory: path to check for python files
    :param prefix: package prefix top add to the file name
    """
    modules = all_modules(directory, prefix, remove_pyc_files)
    for module in modules:
        if module in exclusions:
            print "SKIPPING " + module
        else:
            print module
            __import__(module)


def load_module(name, remove_pyc_files=False, exclusions=[]):
    """
    Loads this modules and all its children

    :param name: name of the modules
    """
    module = __import__(name)
    path = module.__file__
    directory = os.path.dirname(path)
    load_modules(directory, name, remove_pyc_files, exclusions)


if __name__ == '__main__':
    load_module("spinn_utilities", True)
