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

import os
from spinn_utilities.ordered_set import OrderedSet


class ExecutableFinder(object):
    """ Manages a set of folders in which to search for binaries,\
        and allows for binaries to be discovered within this path
    """
    __slots__ = [
        "_binary_search_paths",
        "_binary_log",
        "_paths_log"]

    def __init__(self, binary_search_paths):
        """
        :param iterable(str) binary_search_paths:
            The initial set of folders to search for binaries.
        """
        binary_logs_path = os.environ.get("BINARY_LOGS_DIR", None)
        if binary_logs_path:
            self._paths_log = os.path.join(
                binary_logs_path, "binary_paths_used.log")
            self._binary_log = os.path.join(
                binary_logs_path, "binary_files_used.log")
        else:
            self._paths_log = None
            self._binary_log = None

        self._binary_search_paths = OrderedSet()
        for path in binary_search_paths:
            self.add_path(path)

    def add_path(self, path):
        """ Adds a path to the set of folders to be searched.  The path is\
            added to the end of the list, so it is searched after all the\
            paths currently in the list.

        :param str path: The path to add
        """
        self._binary_search_paths.add(path)
        if self._paths_log:
            try:
                with open(self._paths_log, "a") as log_file:
                    log_file.write(path)
                    log_file.write("\n")
            except Exception:  # pylint: disable=broad-except
                pass

    @property
    def binary_paths(self):
        """ The set of folders to search for binaries, as a printable\
            colon-separated string.

        :rtype: str
        """
        return " : ".join(self._binary_search_paths)

    def get_executable_path(self, executable_name):
        """ Finds an executable within the set of folders. The set of folders\
            is searched sequentially and the first match is returned.

        :param str executable_name: The name of the executable to find
        :return: The full path of the discovered executable
        :rtype: str
        :raises KeyError: If no executable was found in the set of folders
        """
        # Loop through search paths
        for path in self._binary_search_paths:
            # Rebuild filename
            potential_filename = os.path.join(path, executable_name)

            # If this filename exists, return it
            if os.path.isfile(potential_filename):
                if self._binary_log:
                    try:
                        with open(self._binary_log, "a") as log_file:
                            log_file.write(potential_filename)
                            log_file.write("\n")
                    except Exception:  # pylint: disable=broad-except
                        pass
                return potential_filename

        # No executable found
        raise KeyError("Executable {} not found in path".format(
            executable_name))

    def get_executable_paths(self, executable_names):
        """ Finds each executables within the set of folders.

        The names are assumed to be comma separated
        The set of folders is searched sequentially
        and the first match for each name is returned.

        Names not found are ignored and not added to the list.

        :param str executable_names: The name of the executable to find.
            Assumed to be comma separated.
        :return:
            The full path of the discovered executable, or ``None`` if no
            executable was found in the set of folders
        :rtype: list(str)
        """
        results = list()
        for name in executable_names.split(","):
            try:
                results.append(self.get_executable_path(name))
            except KeyError:
                pass
        return results

    def check_logs(self):
        if not self._paths_log:
            print("environ BINARY_LOGS_DIR not set!")
            return

        folders = set()
        with open(self._paths_log, "r") as log_file:
            for line in log_file:
                folders.add(line.strip())

        in_folders = set()
        for folder in folders:
            try:
                for file_name in os.listdir(folder):
                    if file_name.endswith(".aplx"):
                        in_folders.add(os.path.join(folder, file_name))
            except Exception:  # pylint: disable=broad-except
                # Skip folders not found
                pass

        used_binaries = set()
        with open(self._binary_log, "r") as log_file:
            for line in log_file:
                used_binaries.add(line.strip())

        missing = in_folders - used_binaries
        print("{} binaries asked for. {} binaries never asked for.".format(
            len(used_binaries), len(missing)))
        if len(missing) > 0:
            print("Binaries asked for are:")
            for binary in (used_binaries):
                print(binary)
            print("Binaries never asked for are:")
            for binary in (missing):
                print(binary)

    def clear_logs(self):
        if not self._paths_log:
            print("environ BINARY_LOGS_DIR not set!")
            return
        if os.path.isfile(self._paths_log):
            os.remove(self._paths_log)
        if os.path.isfile(self._binary_log):
            os.remove(self._binary_log)


if __name__ == "__main__":
    ef = ExecutableFinder([])
    try:
        ef.check_logs()
        ef.clear_logs()
    except Exception as ex:  # pylint: disable=broad-except
        print(ex)
