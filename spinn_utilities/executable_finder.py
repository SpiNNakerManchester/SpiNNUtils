import os

from spinn_utilities.exceptions import FailedToFindBinaryException
from .ordered_set import OrderedSet


class ExecutableFinder(object):
    """ Manages a set of folders in which to search for binaries,\
        and allows for binaries to be discovered within this path
    """
    __slots__ = [
        "_binary_search_paths"]

    def __init__(self, binary_search_paths):
        """
        :param binary_search_paths:\
            The initial set of folders to search for binaries.
        :type binary_search_paths: iterable of str
        """
        self._binary_search_paths = OrderedSet()
        for path in binary_search_paths:
            self.add_path(path)

    def add_path(self, path):
        """ Adds a path to the set of folders to be searched.  The path is\
            added to the end of the list, so it is searched after all the\
            paths currently in the list.

        :param path: The path to add
        :type path: str
        :return: Nothing is returned
        :rtype: None
        """
        self._binary_search_paths.add(path)

    @property
    def binary_paths(self):
        return " : ".join(self._binary_search_paths)

    def get_executable_path(self, executable_name):
        """ Finds an executable within the set of folders. The set of folders\
            is searched sequentially and the first match is returned.

        :param executable_name: The name of the executable to find
        :type executable_name: str
        :return:\
            The full path of the discovered executable, or ``None`` if no \
            executable was found in the set of folders
        :rtype: str
        """
        # Loop through search paths
        for path in self._binary_search_paths:
            # Rebuild filename
            potential_filename = os.path.join(path, executable_name)

            # If this filename exists, return it
            if os.path.isfile(potential_filename):
                return potential_filename

        # No executable found
        raise FailedToFindBinaryException(
            "failed to locate binary for {}. Fix and try again".format(
                executable_name))

    def get_executable_paths(self, executable_names):
        """ Finds each executables within the set of folders.\

            The names are assumed to be comma separated
            The set of folders is searched sequentially\
            and the first match for each name is returned.

            Names not found are ignored and not added to the list.

        :param executable_names: The name of the executable to find.\
            Assumed to be comma separated.
        :type executable_names: str
        :return:\
            The full path of the discovered executable, or ``None`` if no \
            executable was found in the set of folders
        :rtype: list(str)
        """
        results = list()
        for name in executable_names.split(","):
            path = self.get_executable_path(name)
            if path:
                results.append(path)
        return results
